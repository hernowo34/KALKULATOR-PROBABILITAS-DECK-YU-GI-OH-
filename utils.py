import math

def hitung_peluang(N, K, n, k):
    if k > K or k > n or (n - k) > (N - K):
        return 0.0
    
    kombinasi_target = math.comb(K, k)
    kombinasi_sisa = math.comb(N - K, n - k)
    kombinasi_total = math.comb(N, n)
    
    return (kombinasi_target * kombinasi_sisa) / kombinasi_total

def hitung_peluang_minimal(N, K, n, k):
    peluang_total = 0.0
    maksimal_tarikan = min(K, n)
    
    for i in range(k, maksimal_tarikan + 1):
        peluang_total += hitung_peluang(N, K, n, i)
        
    return peluang_total