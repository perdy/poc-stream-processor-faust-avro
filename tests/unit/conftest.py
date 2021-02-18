from unittest.mock import patch

import pytest

from src.resources import faust_app


@pytest.fixture(scope="session")
def test_app():
    with patch("src.resources.SchemaRegistryClient"):

        faust_app.finalize()
        faust_app.flow_control.resume()

        yield faust_app
