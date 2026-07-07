from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def analyze(self) -> None:
        """Analyze the current market context."""

    @abstractmethod
    def score(self) -> float:
        """Return a normalized opportunity score."""

    @abstractmethod
    def reason(self) -> list[str]:
        """Explain the strategy view."""

    @abstractmethod
    def generate_signal(self) -> None:
        """Generate a signal when conditions are satisfied."""

