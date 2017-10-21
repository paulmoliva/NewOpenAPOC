class BaseModel:
    def as_dict(self):
        result = {}
        for attr, value in self.__dict__.items():
            if not value and value != 0:
                result[attr] = None
            else:
                try:
                    result[attr] = int(value)
                except Exception:
                    try:
                        result[attr] = str(value)
                    except Exception:
                        pass
        return result
