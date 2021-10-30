
def float_map(value: float, leftMin: float, leftMax: float, rightMin: float, rightMax: float) -> float:
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

