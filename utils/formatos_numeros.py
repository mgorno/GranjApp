
def formato_cantidad(n):
    try:
        n = float(n)
        return str(int(n)) if n == int(n) else f"{n:.3f}".rstrip("0").replace(".", ",")
    except (ValueError, TypeError):
        return "0"

def formato_precio(n):
    try:
        n = float(n)
        return f"${int(n)}" if n == int(n) else f"${n:.2f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return "$0"

def formato_precio_arg(value):
    try:
        signo = '-' if value < 0 else ''
        return f"{signo}$ {abs(value):,.0f}".replace(",", ".")
    except:
        return "$ 0"

