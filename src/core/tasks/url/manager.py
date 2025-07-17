import logging

from src.core.tasks.handler import TaskHandler
from src.core.tasks.url.loader import URLTaskOperatorLoader
from src.db.enums import TaskType
from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.core.function_trigger import FunctionTrigger

TASK_REPEAT_THRESHOLD = 20

class TaskManager:

    def __init__(
            self,
            loader: URLTaskOperatorLoader,
            handler: TaskHandler
    ):
        # Dependencies
        self.loader = loader
        self.handler = handler

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)
        self.task_trigger = FunctionTrigger(self.run_tasks)
        self.manager_status: TaskType = TaskType.IDLE


    #region Tasks
    async def set_manager_status(self, task_type: TaskType):
        self.manager_status = task_type

    async def run_tasks(self):
        operators = await self.loader.get_task_operators()
        for operator in operators:
            count = 0
            await self.set_manager_status(task_type=operator.task_type)

            meets_prereq = await operator.meets_task_prerequisites()
            while meets_prereq:
                print(f"Running {operator.task_type.value} Task")
                if count > TASK_REPEAT_THRESHOLD:
                    message = f"Task {operator.task_type.value} has been run more than {TASK_REPEAT_THRESHOLD} times in a row. Task loop terminated."
                    print(message)
                    await self.handler.post_to_discord(message=message)
                    break
                task_id = await self.handler.initiate_task_in_db(task_type=operator.task_type)
                run_info: URLTaskOperatorRunInfo = await operator.run_task(task_id)
                await self.conclude_task(run_info)
                if run_info.outcome == TaskOperatorOutcome.ERROR:
                    break
                count += 1
                meets_prereq = await operator.meets_task_prerequisites()
        await self.set_manager_status(task_type=TaskType.IDLE)

    async def trigger_task_run(self):
        await self.task_trigger.trigger_or_rerun()


    async def conclude_task(self, run_info: URLTaskOperatorRunInfo):
        await self.handler.link_urls_to_task(
            task_id=run_info.task_id,
            url_ids=run_info.linked_url_ids
        )
        await self.handler.handle_outcome(run_info)




