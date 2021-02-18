import pytest

from src.transfer_resources.agent import processor_function
from src.transfer_resources.schema import User


@pytest.mark.type_unit
class TestCaseAgent:
    @pytest.fixture
    def user(self):
        return User.fake()

    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_resource_test_owner_sent_to_kinesis(self, user):
        async with processor_function.test_context() as test_agent:
            await test_agent.put(user)
            # Check that something happens
