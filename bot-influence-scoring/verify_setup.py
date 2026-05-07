import torch

def verify_setup():
    print(f"PyTorch Version: {torch.__version__}")
    
    # Check for MPS (Apple Silicon GPU)
    if torch.backends.mps.is_available():
        print("✅ MPS (Metal Performance Shaders) is available.")
        device = torch.device("mps")
        print(f"Testing tensor on: {device}")
        x = torch.ones(1, device=device)
        print(f"Tensor result: {x}")
    else:
        print("❌ MPS is NOT available.")
        if torch.cuda.is_available():
            print("✅ CUDA is available.")
        else:
            print("Using CPU.")

if __name__ == "__main__":
    verify_setup()
