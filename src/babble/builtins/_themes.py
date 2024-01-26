from babble.themes import Theme
from babble.tuilib.window import RGBColor


class _Themes:
    BABBLE = Theme(
        lambda c, w, h: int(c.x / w * 255),
        lambda c, w, h: 0,
        lambda c, w, h: 255 - int(c.y / h * 255),
    )

    PLASMA = Theme(
        lambda c, w, h: RGBColor.random().red,
        lambda c, w, h: RGBColor.random().green,
        lambda c, w, h: RGBColor.random().blue,
    )

    RADIOACTIVE = Theme(
        lambda c, w, h: int(c.x / w * 255),
        lambda c, w, h: RGBColor.random().green,
        lambda c, w, h: int(c.y / h * 255),
    )

    MONOCHROME = Theme.new_uniform(lambda c, w, h: int(c.x / w * 255))

    @classmethod
    def list(cls) -> dict[str, Theme]:
        return {
            key.lower(): value
            for key, value in cls.__dict__.items()
            if isinstance(value, Theme)
        }

    @classmethod
    def get(cls, name: str) -> Theme | None:
        if name not in cls.list():
            return None

        return cls.get_unchecked(name)

    @classmethod
    def get_unchecked(cls, name: str) -> Theme:
        return cls.list()[name]


themes = _Themes()
