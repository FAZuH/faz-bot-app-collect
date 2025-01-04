from typing import Protocol, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    from faz.bot.wynn.api.base_response import BaseResponse

    type Response = BaseResponse[Any, Any]


class Request(Protocol):
    @property
    def priority(self) -> int: ...
    @property
    def scheduled_time(self) -> datetime:
        """The exact time when the request is scheduled to execute.

        This timestamp indicates when the cached resource will expire 
        and the request should be processed.

        Returns
        -------
        datetime
            The scheduled execution time.
        """
        ...
    @property
    def get_result(self) -> Response: ...
    def is_eligible(self, time: datetime | None= None) -> bool: 
        """

        Parameters
        ----------
        time : datetime | None, optional
            _description_, by default None

        Returns
        -------
        bool
            _description_
        """
        ...
