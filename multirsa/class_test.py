from Crypto.PublicKey.RSA import RsaKey

class RSA_test(RsaKey):
    @RsaKey.n.setter
    def n(self,n):
        self._n = int(n)

