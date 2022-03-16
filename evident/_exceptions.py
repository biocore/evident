import pandas as pd


class WrongPowerArguments(Exception):
    def __init__(
        self,
        alpha: float,
        power: float,
        total_observations: int,
    ):
        args = [alpha, power, total_observations]
        args_msg = self._list_args_msg(*args)

        num_nones = args.count(None)
        if num_nones == 0:
            message = (
                "All arguments were provided. Exactly one of "
                "alpha, power, or total_observations must be None. "
                f"Arguments: {args_msg}"
            )
        elif num_nones == 3:
            message = (
                "No arguments were provided. Exactly one of "
                "alpha, power, or total_observations must be None. "
                f"Arguments: {args_msg}"
            )
        else:
            message = (
                "More than 1 argument was provided. Exactly one of "
                "alpha, power, or total_observations must be None. "
                f"Arguments: {args_msg}"
            )

        super().__init__(message)

    def _list_args_msg(
        self,
        alpha: float,
        power: float,
        total_observations: int,
    ) -> str:
        msg = (
            f"alpha = {alpha}, power = {power}, "
            f"total_observations = {total_observations}."
        )
        return msg


class NonCategoricalColumnError(Exception):
    def __init__(self, column: pd.Series):
        column_dtype = str(column.dtype)
        message = (
            f"Column must be categorical (dtype object). '{column.name}' "
            f"is of type {column_dtype}."
        )
        super().__init__(message)


class OnlyOneCategoryError(Exception):
    def __init__(self, column: pd.Series):
        value = column.dropna().unique().item()
        message = (
            f"Column {column.name} has only one value: '{value}'."
        )
        super().__init__(message)
