import argparse
from parafac2 import parafac2
from data import irregular_tensor
import torch
import gc
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, help='type of running')
    parser.add_argument('-tp', "--tensor_path", type=str)
    parser.add_argument('-op', "--output_path", type=str)
    parser.add_argument('-fp', "--factor_path", type=str)
    parser.add_argument('-r', "--rank", type=int)
    parser.add_argument('-d', "--is_dense", type=str, default="error")
        
    parser.add_argument(
        "-de", "--device",
        action="store", type=int
    )    
    
    parser.add_argument(
        "-b", "--batch_size",
        action="store", default=2**9, type=int
    )
    
    parser.add_argument(
        "-e", "--epoch",
        action="store", type=int
    )
    
    parser.add_argument(
        "-eh", "--epoch_als",
        action="store", type=int, default=500
    )
    
    parser.add_argument(
        "-lr", "--lr", action="store", type=float
    )
    
    parser.add_argument(
        "-cb", "--cluster_batch",
        action="store", default=2**6, type=int
    )
        
    parser.add_argument(
        "-bif", "--batch_init_factor",
        action="store", default=2**6, type=int
    )
    
    parser.add_argument(
        "-tbz", "--tucker_batch_lossz",
        action="store", default=2**6, type=int
    )
    
    parser.add_argument(
        "-tbn", "--tucker_batch_lossnz",
        action="store", default=2**11, type=int
    )
    
    parser.add_argument(
        "-tbu", "--tucker_batch_u",
        action="store", default=2**5, type=int
    )
        
    parser.add_argument(
        "-tbv", "--tucker_batch_v",
        action="store", default=2**6, type=int
    )
    
    parser.add_argument(
        "-tbs", "--tucker_batch_s",
        action="store", default=2**6, type=int
    )
    
    parser.add_argument(
        "-tbg", "--tucker_batch_g",
        action="store", default=2**6, type=int
    )
    
    args = parser.parse_args()    
    if args.is_dense == "True":
        args.is_dense = True
    elif args.is_dense == "False":
        args.is_dense = False
    else:
        assert("wrong input")
    
    device = torch.device("cuda:" + str(args.device))
    _tensor = irregular_tensor(args.tensor_path, device, args.is_dense)
    print("load finish")
    
    _parafac2 = parafac2(_tensor, device, args)        
    if args.action == "train":
        if os.path.exists(args.output_path + "_cp.pt"):
            checkpoint = torch.load(args.output_path + "_cp.pt")
            
            _parafac2.centroids.data.copy_(checkpoint['centroids'].to(device))
            _parafac2.U.data.copy_(checkpoint['U'].to(device))
            _parafac2.V.data.copy_(checkpoint['V'].to(device))
            _parafac2.S.data.copy_(checkpoint['S'].to(device))
        else:
            _parafac2.quantization(args)
        #gc.collect()
        #torch.cuda.empty_cache()    
        _parafac2.als(args)
    elif args.action == "test_loss":
        with torch.no_grad():
            print(f'sparse: {_parafac2.L2_loss(False, args.batch_size, _parafac2.U)}')
            for i in range(_tensor.k):
                _tensor.src_tensor[i] = _tensor.src_tensor[i].todense()
            print(f'dense: {_parafac2.L2_loss_dense(False, args.batch_size, _parafac2.U)}')
            