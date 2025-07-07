import atexit
import os
import threading

from pydantic import BaseModel, Field
from tinydb import TinyDB

from core.cache import mkdir


class Entity(BaseModel):
    """
    Entities are the primary nodes in the knowledge graph. Each entity has:

    A unique name (identifier)
    An entity type (e.g., "person", "organization", "event")
    A list of observations
    """

    name: str = Field(description="名称", examples=["John_Smith"])
    entity_type: str = Field(
        description="实体类型", examples=["person", "organization", "event"]
    )
    observations: list[str] = Field(
        description="观察",
        examples=[["John_Smith is a person", "John_Smith works at Google"]],
    )


class Relation(BaseModel):
    """
    Relations define directed connections between entities. They are always stored in active voice and describe how entities interact or relate to each other.
    """

    from_entity: str = Field(description="源实体", examples=["John_Smith"])
    to_entity: str = Field(description="目标实体", examples=["Google"])
    relation_type: str = Field(
        description="关系类型", examples=["works_for", "knows", "attended"]
    )


class Observation(BaseModel):
    """
    Observations are discrete pieces of information about an entity. They are:

    Stored as strings
    Attached to specific entities
    Can be added or removed independently
    Should be atomic (one fact per observation)
    """

    entity_name: str = Field(description="实体名称", examples=["John_Smith"])
    observations: list[str] = Field(
        description="观察",
        examples=[["John_Smith is a person", "John_Smith works at Google"]],
    )


class Manager(object):
    def __init__(self):
        self.lock = threading.Lock()
        filename = os.path.join("cache", "task", "manager.json")
        mkdir(os.path.dirname(filename))
        self.db = TinyDB(filename, encoding="utf-8")
        atexit.register(self.db.close)

    def get_table(self, table_name: str):
        return self.db.table(table_name)

    def get_entity_table(self, namespace: str):
        return self.get_table("{}.entity".format(namespace))

    def get_relation_table(self, namespace: str):
        return self.get_table("{}.relation".format(namespace))

    def add_entities(self, namespace: str, entities: list[Entity]):
        with self.lock:
            self.get_entity_table(namespace).insert_multiple(
                [entity.model_dump() for entity in entities]
            )

    def delete_entities(self, namespace: str, entities_names: list[str]):
        with self.lock:
            self.get_entity_table(namespace).remove(
                lambda entity: entity["name"] in entities_names
            )

    def add_relations(self, namespace: str, relations: list[Relation]):
        with self.lock:
            self.get_relation_table(namespace).insert_multiple(
                [relation.model_dump() for relation in relations]
            )

    def delete_relations(self, namespace: str, relations: list[Relation]):
        with self.lock:
            self.get_relation_table(namespace).remove(
                lambda relation: relation["from_entity"]
                in [relation.from_entity for relation in relations]
                and relation["to_entity"]
                in [relation.to_entity for relation in relations]
                and relation["relation_type"]
                in [relation.relation_type for relation in relations]
            )

    def _get_or_create_entity(self, namespace: str, entity_name: str):
        table = self.get_entity_table(namespace)
        if not table.contains(lambda name: name == entity_name):
            table.insert(
                Entity(
                    name=entity_name,
                    entity_type="unknown",
                    observations=[],
                ).model_dump()
            )

        return table.get(lambda name: name == entity_name)

    def add_observations(self, namespace: str, observations: list[Observation]):
        with self.lock:
            table = self.get_entity_table(namespace)
            for observation in observations:
                old_entity = self._get_or_create_entity(
                    namespace, observation.entity_name
                )
                if old_entity["observations"] is None:
                    old_entity["observations"] = []

                old_entity["observations"].extend(observation.observations)
                old_entity["observations"] = list(set(old_entity["observations"]))
                table.update(old_entity, lambda entity_name: entity_name)

    def delete_observations(self, namespace: str, observations: list[Observation]):
        """
        遍历 observations 中的每一个 entity_name 中的 observations，并移除当中的 observations

        :param namespace:
        :param observations:
        :return:
        """
        with self.lock:
            table = self.get_entity_table(namespace)
            for observation in observations:
                old_entity = self._get_or_create_entity(
                    namespace, observation.entity_name
                )
                if old_entity["observations"] is None:
                    old_entity["observations"] = []

                old_entity["observations"] = [
                    observation
                    for observation in old_entity["observations"]
                    if observation not in observation.observations
                ]
                table.update(old_entity, lambda entity_name: entity_name)

    def get_entities(self, namespace: str):
        with self.lock:
            return self.get_entity_table(namespace).all()

    def get_relations(self, namespace: str):
        with self.lock:
            return self.get_relation_table(namespace).all()

    def get_graph(self, namespace: str):
        with self.lock:
            return {
                "entities": self.get_entity_table(namespace).all,
                "relations": self.get_relation_table(namespace).all,
            }

    def clear(self, namespace: str):
        with self.lock:
            self.get_entity_table(namespace).truncate()
            self.get_relation_table(namespace).truncate()


manager = Manager()