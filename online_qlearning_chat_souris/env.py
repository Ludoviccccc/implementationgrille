import torch
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence
import torch.nn as nn
import numpy as np

class grid:
    """
    Envirnonement grille sur laquelle se deplace l'agent jusqu'à atteindre le point G
    """
    def __init__(self,Nx,Ny, G = 50,gamma = .9,S = 3,C= 12,epsilon=0.05):
        assert(0<=G<Nx*Ny)
        self.actions = [(0,1), (0, -1), (1, 0), (-1, 0)]
        self.epsilon = epsilon
        self.Na = len(self.actions)
        self.Nx = Nx
        self.Ny = Ny
        self.R = -1
        self.G = G
        self.gamma = gamma
        self.S = S
        self.C = C
        self.states_encod = torch.eye(self.Nx*self.Ny).unsqueeze(0)
        self.actions_encod = torch.eye(self.Na).unsqueeze(0)
    def reset(self):
        self.S = torch.randint(0,self.Nx*self.Ny,(1,))
        self.C = torch.randint(0,self.Nx*self.Ny,(1,))
#    def transition_chat(self,a):
#        assert(0<=sp[0]*self.Ny+sp[1]<self.Nx*self.Ny)
#        out = sp[0]*self.Ny+sp[1]  
#        return out
    def transition(self,a,s):
        assert(0<=s<self.Nx*self.Ny)
        d = self.actions[a]
        s_couple = (s//self.Ny, s%self.Ny)
        if self.Nx>s_couple[0]+ d[0]>=0 and self.Ny>s_couple[1]+d[1]>=0:
            sp = (s_couple[0]+ d[0], s_couple[1]+d[1])
            assert(0<=sp[0]*self.Ny+sp[1]<self.Nx*self.Ny)
            s_out = sp[0]*self.Ny+sp[1]
            return s_out
        return s
    def reward_chat(self,S,C):
        return S == C
    def reward_souris(self,S,C):
        return (-1)*(S == C)
    def grid(self,s_souris,s_chat):
        #assert(type(s)==int)
        #assert(0<=s<=self.Nx*self.Ny)
        T = np.zeros((self.Nx,self.Ny))
        #T[self.G//self.Ny, self.G%self.Ny] = 6
        T[s_souris//self.Ny, s_souris%self.Ny] = 1
        T[s_chat//self.Ny, s_chat%self.Ny] = -1
        #T[s//self.Ny, s%self.Ny] = 1
        print(T)
    def tensor_state(self,s):
        return self.states_encod[:,:,s]
    def zero_one(self,state,J):
        x = nn.functional.one_hot(state,J)
        x = x.reshape((len(state),-1))
        x = x.type(torch.float32)
        return x
    def representation_action(self,a):
        return torch.Tensor([self.actions[i][0] for i in a]), torch.Tensor([self.actions[i][1] for i in a])
    def transitionvec(self,a,s):
        "a un est un iterable de valeurs scalaires"
        "s un est un iterable de valeurs scalaires"
        couples = {0:s//self.Ny,1:s%self.Ny}
        mouv1,mouv2 = self.representation_action(a)
        A =(couples[0]+mouv1>=0)*(couples[0]+mouv1<self.Nx)*(couples[1]+mouv2>=0)*(couples[1]+mouv2<self.Ny)
        couples2 = {0:(couples[0]+mouv1)*A,
                    1:(couples[1]+mouv2)*A
                    }
        newstate = couples2[0]*self.Ny+couples2[1]
        reward = (newstate==self.G)#+(A*(-1)+1)*(-10)
        return newstate,reward
    def representation(self,s,c):
        out1 = (-1)*pad_sequence([self.states_encod[0,:,int(i)] for i in c]).permute(1,0)
        out2 =      pad_sequence([self.states_encod[0,:,int(i)] for i in s]).permute(1,0)
        return out1+out2
    def representationaction(self,action):
        return  pad_sequence([self.actions_encod[0,:,int(i)] for i in action]).permute(1,0)
