import pytest
from llamapay.constants import DURATION_TO_SECONDS
from llamapay import Rate


def test_duration():
    # https://github.com/LlamaPay/interface/blob/main/utils/constants.ts#L282
    assert DURATION_TO_SECONDS["day"] == 86_400
    assert DURATION_TO_SECONDS["week"] == 604_800
    assert DURATION_TO_SECONDS["month"] == 2_592_000
    assert DURATION_TO_SECONDS["year"] == 31_104_000


@pytest.mark.parametrize(
    "rate",
    [
        "1000000/year",
        "100,000 UNI/day",
        "10_000 USDC/month",
        "10 YFI/year",
    ],
)
def test_rate(rate):
    r = Rate.parse(rate)
    print(r)
    print(repr(r))
