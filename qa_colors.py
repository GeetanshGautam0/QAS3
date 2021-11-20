import re, qa_std


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


class Functions:
    @staticmethod
    def fade(start: str, end: str):
        stRGB = Convert.HexToRGB(start)
        edRGB = Convert.HexToRGB(end)

        # Deltas
        deltas_pol = (*[((edRGB[i] - stRGB[i])/abs(edRGB[i] - stRGB[i])) if (edRGB[i] - stRGB[i]) != 0 else 1 for i in range(3)], )
        deltas = (*[abs(edRGB[i] - stRGB[i]) for i in range(3)], )
        steps = sorted(deltas)[-1]
        o = [start]

        for step in range(steps):
            # o = [*o, (*[(int(clamp(0, o[step-1][j] + deltas[j]/steps, 255))) for j in range(3)], )]
            # o = [*o, (*[(int(clamp(0, (stRGB[j] + (deltas[j] / steps * step)), 255))) for j in range(3)], )]

            o = (*o,
                 Convert.RGBToHex(
                     (*[
                         (int(clamp(
                             0,
                             (stRGB[j] + (deltas[j]*deltas_pol[j] / steps * step)),
                             255)
                         )) for j in range(3)
                     ],))
                 )

        # o = (*[Convert.RGBToHex(i) for i in o], end)
        o = (*o, end)
        return o

    @staticmethod
    def calculate_more_contrast(one, two, color):
        # o = Convert.HexToInt(one)
        # t = Convert.HexToInt(two)
        # c = Convert.HexToInt(color)
        # max_diff = sorted((abs(c - o), abs(c - t)))[-1]
        # m = {abs(c - o): one, abs(c - t): two}
        # f = m[max_diff]
        # m.pop(max_diff)
        # g = (*m.values(), )[0]

        f, g = one, two

        if not std.check_hex_contrast(f, color)[0]:
            if std.check_hex_contrast(g, color)[0]:
                return g
        return f


def clamp(minimum: int, actual: int, maximum: int) -> int:
    return minimum if (actual < minimum) else (maximum if (actual > maximum) else actual)