# File: backend/controller/tag_controller.py

from litestar import Controller, get
from typing import List

# We will import the new tag service we are about to create
from services.tag_service import tag_service

class TagController(Controller):
    path = "/api/tags"

    @get("/all")
    async def get_all_tags(self) -> List[str]:
        """
        Returns a de-duplicated, alphabetized list of all tags in the system.
        This result is cached for performance.
        """
        all_tags = await tag_service.get_all_tags()
        return all_tags