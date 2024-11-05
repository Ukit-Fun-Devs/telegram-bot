class GroupInfo:
    def __init__(self, data: dict[str, dict | str]) -> None:
        self.raw: dict[str, str | dict] = data["data"]

        self.faculty = self.raw.get("faculName")
        self.department = self.raw.get("kafName")
        self.form = self.raw.get("formName")
        self.level = self.raw.get("levelName")
        self.years = self.raw.get("groupYear")

        group: dict = self.raw["group"]
        self.text_id = group.get("item1")
        self.id = group.get("item2")

        self.course = int(self.raw.get("course"))
        self.special = self.raw.get("specialName")

        self.students_count = len(self.raw.get("studentInfoGroup"))
