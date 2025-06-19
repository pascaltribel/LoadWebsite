import torch
import torch.nn as nn

class ConvFeatureExtractor(nn.Module):
    def __init__(self, mlp_size):
        super(ConvFeatureExtractor, self).__init__()
        self.dropout = nn.Dropout(0.1)
        self.conv = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, padding="same")
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=1, kernel_size=3, padding="same")
        self.l1 = nn.Linear(mlp_size, 512)
        self.l2 = nn.Linear(512, 256)
        self.l3 = nn.Linear(256, 16)
        self.activation = nn.Tanh()
    
    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.dropout(self.conv(x))
        x = self.dropout(self.activation(x))
        x = self.dropout(self.conv2(x))
        x = self.dropout(self.activation(x.reshape((x.shape[0], -1))))
        x = self.dropout(self.activation(self.l1(x)))
        x = self.dropout(self.activation(self.l2(x)))
        x = self.l3(x)
        return x
            
class ForecastModel(nn.Module):
    def __init__(self):
        super(ForecastModel, self).__init__()
        self.dropout = nn.Dropout(0.05)
        self.feature_extractor_load = ConvFeatureExtractor(mlp_size=2016)
        self.feature_extractor_meteo = ConvFeatureExtractor(mlp_size=2688)
        self.l1 = nn.Linear(16*2, 16)
        self.l2 = nn.Linear(16, 1)
        self.relu = nn.ELU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x_load, x_meteo, x_baseline):
        x = self.l1(torch.concatenate([self.relu(self.feature_extractor_load(x_load)), 
                                       self.relu(self.feature_extractor_meteo(x_meteo))], axis=1))
        x = 2*self.sigmoid(self.l2(self.dropout(self.relu(x))))
        return (x * (x_baseline)).squeeze()