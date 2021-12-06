class CallbackKeyEncoder:
    @staticmethod
    def enc_cb_data(key: str, value: str) -> str:
        assert len(key.split('__')) == 1 and len(value.split('__')) == 1
        return f'{key}__{value}'

    @staticmethod
    def dec_cb_data(token: str) -> (str, str):
        return token.split('__')[0], token.split('__')[1]

    @staticmethod
    def enc_void(key: str, value: str) -> str:
        return f'void__{key}#{value}'

    @staticmethod
    def decode_void(token: str) -> (str, str):
        return token.split('__')[1].split('#')[0], token.split('__')[1].split('#')[1]
