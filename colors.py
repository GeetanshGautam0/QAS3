import re
from time import sleep


class Convert:
    @staticmethod
    def HexToRGB(Hex: str):
        return tuple(int("".join(i for i in re.findall(r"\w", Hex))[j:j+2], 16) for j in (0, 2, 4))

    @staticmethod
    def RGBToInt(rgb: tuple):
        return rgb[0] << 16 | rgb[1] << 8 | rgb[2]

    @staticmethod
    def IntToRGB(irgb: int):
        return irgb // 256 // 256 % 256, irgb // 256 % 256 // irgb // 256

    @staticmethod
    def RGBToHex(rgb: tuple):
        return "#%02x%02x%02x" % rgb

    @staticmethod
    def HexToInt(Hex: str):
        return Convert.RGBToInt(Convert.HexToRGB("".join(i for i in re.findall(r"\w", Hex))))

    @staticmethod
    def IntToHex(Int: int):
        return Convert.RGBToHex(Convert.IntToRGB(Int))


class Fade:
    @staticmethod
    def mono(start: str, end: str):
        stRGB = Convert.HexToRGB(start)
        edRGB = Convert.HexToRGB(end)

        # Deltas
        deltas = (*[edRGB[i] - stRGB[i] for i in range(3)], )
        steps = abs(sorted(deltas)[-1])
        o = [start]

        for step in range(steps):
            # o = [*o, (*[(int(clamp(0, o[step-1][j] + deltas[j]/steps, 255))) for j in range(3)], )]
            # o = [*o, (*[(int(clamp(0, (stRGB[j] + (deltas[j] / steps * step)), 255))) for j in range(3)], )]

            o = (*o, Convert.RGBToHex((*[(int(clamp(0, (stRGB[j] + (deltas[j] / steps * step)), 255))) for j in range(3)],)))

        # o = (*[Convert.RGBToHex(i) for i in o], end)
        o = (*o, end)
        return o


def clamp(minimum: int, actual: int, maximum: int) -> int:
    return minimum if actual < minimum else maximum if actual > maximum else actual
