#
# Blue Brain Nexus Forge is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Blue Brain Nexus Forge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Blue Brain Nexus Forge. If not, see <https://choosealicense.com/licenses/lgpl-3.0/>.

# Placeholder for the test suite for actions.
import pytest

from kgforge.core import Resource, KnowledgeGraphForge
from kgforge.core.archetypes.store import rewrite_sparql
from kgforge.core.commons.exceptions import DownloadingError, FreezingError
from kgforge.specializations.resources import Dataset
from kgforge.core.wrappings.dict import DictWrapper, wrap_dict
import json

context = {
    "@context": {
        "type": {
            "@id": "rdf:type",
            "@type": "@id"
        },
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "prov": "http://www.w3.org/ns/prov#",
        "schema": "http://schema.org/",
        "Person": {
            "@id": "schema:Person",
            "@type": "@id"
        },
        "Association": "prov:Association",
        "name": "schema:name",
        "agent": "prov:agent",
        "description": "http://schema.org/description",
    }
}


prefixes = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "prov": "http://www.w3.org/ns/prov#",
    "schema": "http://schema.org/",
}


prefixes_string = "\n".join([f"PREFIX {k}: <{v}>" for k, v in prefixes.items()])


form_store_metadata_combinations = [
    ("SELECT ?agent WHERE { <http://exaplpe.org/1234> agent ?agent }",
     prefixes_string + "\nSELECT ?agent WHERE { <http://exaplpe.org/1234> prov:agent ?agent }"),
    ("SELECT ?agent WHERE { ?agent type ?v0 FILTER(?v0 != Person) }",
     prefixes_string + "\nSELECT ?agent WHERE { ?agent rdf:type ?v0 FILTER(?v0 != schema:Person) }"),
    ("SELECT ?x ?name WHERE { ?x type Association ; agent/name ?name }",
     prefixes_string + "\nSELECT ?x ?name WHERE { ?x rdf:type prov:Association ; prov:agent/schema:name ?name }"),
    ("SELECT ?name WHERE { ?x agent/name ?name FILTER regex(?name, \"^j\", \"i\") }",
     prefixes_string + "\nSELECT ?name WHERE { ?x prov:agent/schema:name ?name FILTER regex(?name, \"^j\", \"i\") }"),
    ("SELECT ?x WHERE { <http://exaplpe.org/1234> description ?x }",
     prefixes_string + "\nSELECT ?x WHERE { <http://exaplpe.org/1234> <http://schema.org/description> ?x }"),
]


@pytest.mark.parametrize("query, expected", form_store_metadata_combinations)
def test_rewrite_sparql(query, expected):
    result = rewrite_sparql(query, context, prefixes)
    assert result == expected


def test_download(config):
    simple = Resource(type="Experiment", url="file.gz")
    with pytest.raises(DownloadingError):
        forge = KnowledgeGraphForge(config)
        forge._store.download(simple, "fake.path", "./", overwrite=False)

def test_freeze(config, store_metadata_value):

    forge = KnowledgeGraphForge(config, debug=True)
    derivation1 = Dataset(forge, type="Dataset", name="A derivation dataset")
    derivation1.id = "http://derivation1"
    derivation1._store_metadata = wrap_dict(store_metadata_value)

    generation1 = Dataset(forge, type="Dataset", name="A generation dataset")
    generation1.id = "http://generation1"
    generation1._store_metadata = wrap_dict(store_metadata_value)

    invalidation1 = Dataset(forge, type="Activity", name="An invalidation activity")
    invalidation1.id = "http://invalidation1"
    invalidation1._store_metadata = wrap_dict(store_metadata_value)

    contribution1 = Resource(type="Person", name="A contributor")
    contribution1.id = "http://contribution1"
    contribution1._store_metadata = wrap_dict(store_metadata_value)

    dataset = Dataset(forge, type="Dataset", name="A dataset")
    dataset._store_metadata = wrap_dict(store_metadata_value)
    dataset.add_derivation(derivation1, versioned=False)
    dataset.add_generation(generation1, versioned=False)
    dataset.add_invalidation(invalidation1, versioned=False)
    dataset.add_contribution(contribution1, versioned=False)

    expected_derivation = json.loads(json.dumps({"type":"Derivation", "entity":{"id": "http://derivation1",
                                                                                "type":"Dataset", "name":"A derivation dataset"}}))
    assert forge.as_json(dataset.derivation) == expected_derivation

    expected_generation = json.loads(json.dumps({"type": "Generation",
                                                 "activity": {"id": "http://generation1", "type": "Dataset"}}))
    assert forge.as_json(dataset.generation) == expected_generation

    expected_contribution = json.loads(json.dumps({"type": "Contribution",
                                                 "agent": {"id": "http://contribution1", "type": "Person"}}))
    assert forge.as_json(dataset.contribution) == expected_contribution

    expected_invalidation = json.loads(json.dumps({"type": "Invalidation",
                                                   "activity": {"id": "http://invalidation1", "type": "Activity"}}))
    assert forge.as_json(dataset.invalidation) == expected_invalidation

    dataset.id = "http://dataset"
    dataset._synchronized = True
    forge._store.freeze(dataset)
    assert dataset.id == "http://dataset?_version=1"
    assert dataset.derivation.entity.id == "http://derivation1?_version=1"
    assert dataset.generation.activity.id == "http://generation1?_version=1"
    assert dataset.contribution.agent.id == "http://contribution1?_version=1"
    assert dataset.invalidation.activity.id == "http://invalidation1?_version=1"
