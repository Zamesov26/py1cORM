class _NotLoadedType:
    __slots__ = ()

    def __repr__(self) -> str:
        return 'NotLoaded'

    def __bool__(self) -> bool:
        # чтобы NotLoaded не вел себя как True в if
        return False


NotLoaded = _NotLoadedType()
