"""Test all the methods in the Raindrop Collection API."""
from raindropiopy import User
from raindropiocli.models.raindrop_state import RaindropState
from tests.conftest import vcr


@vcr.use_cassette()
def test_raindrop_state(api) -> None:
    """Test that we instantiate a new Raindrop state instance from Raindrop."""
    user = User.get(api)
    state = RaindropState(api, user=user)
    state.refresh()
