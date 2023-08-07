import argparse
from parafac2 import parafac2
from data import irregular_tensor
import torch

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-tp', "--tensor_path", type=str)
    parser.add_argument('-op', "--output_path", type=str)
    parser.add_argument('-fp', "--factor_path", type=str)
    
    parser.add_argument(
        "-de", "--device",
        action="store", type=int
    )    
    
    parser.add_argument(
        "-b", "--batch_size",
        action="store", default=2**21, type=int
    )
    
    parser.add_argument(
        "-e", "--epoch",
        action="store", type=int
    )
    
    parser.add_argument(
        "-lr", "--lr", action="store", type=float
    )
    
    args = parser.parse_args()    
    device = torch.device("cuda:" + str(args.device))
    _tensor = irregular_tensor(args.tensor_path, device)
    print("load finish")
    
    _parafac2 = parafac2(_tensor, device, args)
    _parafac2.quantization(args)