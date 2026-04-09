import random

def generate_benchmark_array(n, min_val=1, max_val=1000):
    """
    Generates a random array of size N and prints it in a C-friendly format.
    """
    # Generate an array of random integers
    random_array = [random.randint(min_val, max_val) for _ in range(n)]
    
    # Format and print the output
    print(f"// Size: N = {n}")
    print("{" + ", ".join(map(str, random_array)) + "};")

if __name__ == "__main__":
    # Change this value to generate different sizes (e.g., 10000, 100000)
    N = 5000
    
    generate_benchmark_array(N)