from sqlmodel import Field, SQLModel, Session, create_engine, select, col, Relationship
from fastapi import FastAPI
from contextlib import asynccontextmanager

# model

class MilestoneGroup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    milestones: list["Milestone"] = Relationship(back_populates="group")

class MilestoneBase(SQLModel):
    group_id: int | None = Field(default=None, foreign_key="milestonegroup.id")
    title: str
    image: str
    text: str
    priority: int | None = None
    group: MilestoneGroup = Relationship(back_populates="milestones")

class Milestone(MilestoneBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class MilestoneCreate(MilestoneBase):
    pass

class MilestonePublic(MilestoneBase):
    id: int

class MilestoneTr(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

# database

engine = create_engine("sqlite:///milestones.db", echo=True, connect_args={"check_same_thread": False})

def create():
    SQLModel.metadata.create_all(engine)
    add()

def add():
    with Session(engine) as session:
        g1 = MilestoneGroup(title="Group 1", description="Description 1")
        g2 = MilestoneGroup(title="Group 2", description="Description 2")
        session.add(g1)
        session.add(g2)
        m1 = Milestone(title="1", group=g1, image="image1.jpg", text="text1", priority=1)
        m2 = Milestone(title="2", group=g1, image="image2.jpg", text="text2", priority=2)
        m3 = Milestone(title="2", group=g2, image="image2.jpg", text="text2", priority=2)
        session.add(m3)
        session.add(m2)
        session.add(m1)
        session.commit()

def read():
    with Session(engine) as session:
        groups = session.exec(select(MilestoneGroup)).all()
        for group in groups:
            print(group)
            print(group.milestones)
            print()

def update():
    with Session(engine) as session:
        milestone = session.get(Milestone, 3)
        milestone.title = "Updated title"
        session.add(milestone)
        session.commit()
        session.refresh(milestone)

# app

@asynccontextmanager
async def lifespan(app: FastAPI):
    create()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/milestones/", response_model=MilestonePublic)
def create_milestone(milestone: MilestoneCreate):
    with Session(engine) as session:
        session.add(milestone)
        session.commit()
        session.refresh(milestone)
        return milestone


@app.get("/milestones/", response_model=list[MilestonePublic])
def read_milestones():
    with Session(engine) as session:
        milestones = session.exec(select(Milestone)).all()
        return milestones
#
#
# if __name__ == "__main__":
#     # create()
#     update()
#     read()