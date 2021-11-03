import wcag_contrast_ratio, re


def float_map(value: float, input_min: float, input_max: float, output_min: float, output_max: float) -> float:
    """
    **FLOAT_MAP**

    Takes in float 'value' between points 'input_min' and 'input_max' and scales it to fit into the output range (output_min >> output_max)

    :param value: Actual Value
    :param input_min: Input range (min)
    :param input_max: Input range (max)
    :param output_min: Output range (min)
    :param output_max: Output range (max)
    :return: mapped float
    """

    leftSpan = input_max - input_min
    rightSpan = output_max - output_min
    valueScaled = float(value - input_min) / float(leftSpan)
    return output_min + (valueScaled * rightSpan)


def check_hex_contrast(bg, fg) -> tuple:
    """
    **CHECK_HEX_CONTRAST**

    Takes in colors 1 and 2 ('bg' and 'fg') and decides whether if there is enough contrast.

    :param bg: Color 1 (HEX)
    :param fg: Color 2 (HEX)
    :return: Tuple (Passes WCAG AA?, Passes WCAG AAA?, (BG, FG))
    """

    contrast = ()

    def map_rgb(color_rgb: tuple) -> tuple:
        assert len(color_rgb) == 3
        o_tuple = ()

        for col in color_rgb:
            o_tuple = (*o_tuple, float_map(col, 0.00, 255.00, 0.00, 1.00))

        return o_tuple

    def hex_to_rgb(Hex: str) -> tuple:
        return tuple(int("".join(i for i in re.findall(r"\w", Hex))[j:j + 2], 16) for j in (0, 2, 4))

    back = hex_to_rgb(bg)
    front = hex_to_rgb(fg)

    AA_res = wcag_contrast_ratio.passes_AA(wcag_contrast_ratio.rgb(map_rgb(back), map_rgb(front)))
    AAA_res = wcag_contrast_ratio.passes_AAA(wcag_contrast_ratio.rgb(map_rgb(back), map_rgb(front)))

    return AA_res, AAA_res, (bg, fg)


def data_at_dict_path(path: str, dictionary: dict) -> tuple:
    """
    **DATA_AT_DICT_PATH**

    Takes in dictionary 'dictionary' and finds data at path 'path'

    :param path: Path in dict (entries separated by '/' or '\\')
    :param dictionary: Data dictionary
    :return: Tuple (found?, data)
    """

    assert isinstance(path, str), "Invalid path input"
    assert isinstance(dictionary, dict), "Invalid dict input"

    path = path.replace('/', '\\')
    path_tokens = (*path.split('\\'), )

    found = True
    data = {**dictionary}

    for index, token in enumerate(path_tokens):
        if token == "root" and index == 0:
            continue

        found = token in data
        data = data.get(token)
        if index != len(path_tokens) - 1:
            if type(data) is not dict:
                found = False

        if not found:
            break

    return found, data

