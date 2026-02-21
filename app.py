from flask import Flask, request, jsonify, send_from_directory
from rdflib import Graph
from flask_cors import CORS
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__, static_folder="static")
CORS(app)
asgi_app = WsgiToAsgi(app)

# ── Load ontology ──────────────────────────────────────────────
OWL_FILE = "./Faculty_Ontology.ttl"
print(f"Loading ontology: {OWL_FILE}...")

g = Graph()
try:
    g.parse("Faculty_Ontology.ttl", format="turtle")
    print(f"Success! Loaded {len(g)} triples.")
except Exception as e:
    print(f"Error found: {e}")

print(f"Done — {len(g)} triples loaded.")

PREFIX = """
PREFIX : <http://www.semanticweb.org/hevindutilakasena/ontologies/2026/1/untitled-ontology-13#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

# ── 20 Competency Questions ────────────────────────────────────
QUESTIONS = [
    {
        "id": 1,
        "question": "What courses are offered under the BSc (Hons) in Artificial Intelligence program?",
        "sparql": PREFIX + """
SELECT ?courseCode ?courseName ?credits ?courseType
WHERE {
    ?program :hasProgramName "Bsc (Hons) in AI" .
    ?program :containCourses ?course .
    ?course :hasCourseCode ?courseCode ;
            :hasCourseName  ?courseName ;
            :hasNumberOfCredits ?credits ;
            :hasCourseType  ?courseType .
}
ORDER BY ?courseCode"""
    },
    {
        "id": 2,
        "question": "Which department offers each program?",
        "sparql": PREFIX + """
SELECT ?programName ?deptName
WHERE {
    ?program rdf:type/rdfs:subClassOf* :Program ;
             :hasProgramName ?programName .
    ?dept :offersProgram ?program .
    BIND(REPLACE(STR(?dept), "^.*#", "") AS ?deptName)
}
ORDER BY ?programName"""
    },
    {
        "id": 3,
        "question": "What are all elective courses available across all programs?",
        "sparql": PREFIX + """
SELECT DISTINCT ?courseCode ?courseName ?credits
WHERE {
    ?course a :Course ;
            :hasCourseCode ?courseCode ;
            :hasCourseName ?courseName ;
            :hasNumberOfCredits ?credits ;
            :hasCourseType "Elective" .
}
ORDER BY ?courseCode"""
    },
    {
        "id": 4,
        "question": "Which academic staff teach which courses?",
        "sparql": PREFIX + """
SELECT ?staffName ?position ?courseCode ?courseName
WHERE {
    ?staff a :AcademicStaff ;
           :hasPersonName ?staffName ;
           :hasPosition    ?position ;
           :teaches        ?course .
    ?course :hasCourseCode ?courseCode ;
            :hasCourseName  ?courseName .
}
ORDER BY ?staffName"""
    },
    {
        "id": 5,
        "question": "Which students belong to the Department of Computational Mathematics?",
        "sparql": PREFIX + """
SELECT ?studentName ?registrationNumber
WHERE {
  BIND(:Department_of_Computational_Mathematics AS ?dept)
  ?dept :offersProgram ?program .
  ?program :hasEnrolledStudents ?student .
  ?student :hasPersonName ?studentName .
  ?student :hasRegistrationNumber ?registrationNumber .
}"""
    },
    {
        "id": 6,
        "question": "Who is the advisor of each student?",
        "sparql": PREFIX + """
SELECT ?studentName ?advisorName
WHERE {
  ?student :hasAdvisor ?advisor .
  ?student :hasPersonName ?studentName .
  ?advisor :hasPersonName ?advisorName .
}"""
    },
    {
        "id": 7,
        "question": "What are all undergraduate programs offered by the faculty?",
        "sparql": PREFIX + """
SELECT ?programName ?duration
WHERE {
    ?program a :UndergraduateProgram ;
             :hasProgramName     ?programName ;
             :hasProgramDuration ?duration .
}
ORDER BY ?programName"""
    },
    {
        "id": 8,
        "question": "What are all postgraduate programs offered by the faculty?",
        "sparql": PREFIX + """
SELECT ?programName ?duration
WHERE {
    ?program a :PostgraduateProgram ;
             :hasProgramName     ?programName ;
             :hasProgramDuration ?duration .
}
ORDER BY ?programName"""
    },
    {
        "id": 9,
        "question": "Which courses have lab hours?",
        "sparql": PREFIX + """
SELECT ?courseCode ?courseName ?lectureHours ?labHours
WHERE {
    ?course a :Course ;
            :hasCourseCode ?courseCode ;
            :hasCourseName ?courseName ;
            :hasLabHours   ?labHours .
    OPTIONAL { ?course :hasLectureHours ?lectureHours . }
}
ORDER BY ?courseCode"""
    },
    {
        "id": 10,
        "question": "What is the total number of credits in each program?",
        "sparql": PREFIX + """
SELECT ?programName (SUM(?credits) AS ?totalCredits)
WHERE {
    ?program :hasProgramName ?programName ;
             :containCourses ?course .
    ?course  :hasNumberOfCredits ?credits .
}
GROUP BY ?program ?programName
ORDER BY ?programName"""
    },
    {
        "id": 11,
        "question": "Which courses appear in more than one program?",
        "sparql": PREFIX + """
SELECT ?courseCode ?courseName (COUNT(?program) AS ?numPrograms)
WHERE {
    ?program :containCourses ?course .
    ?course  :hasCourseCode ?courseCode ;
             :hasCourseName  ?courseName .
}
GROUP BY ?course ?courseCode ?courseName
HAVING (COUNT(?program) > 1)
ORDER BY DESC(?numPrograms)"""
    },
    {
        "id": 12,
        "question": "Which academic staff belong to the Department of Information Technology?",
        "sparql": PREFIX + """
SELECT ?staffName ?position ?email
WHERE {
    ?staff a :AcademicStaff ;
           :hasPersonName ?staffName ;
           :hasPosition   ?position ;
           :hasEmail      ?email ;
           :isMemberOf :Department_of_Information_Technology .
}
ORDER BY ?staffName"""
    },
    {
        "id": 13,
        "question": "What programs does each department offer?",
        "sparql": PREFIX + """
SELECT ?dept ?programName ?duration
WHERE {
    ?dept a :Department ;
          :offersProgram ?program .
    ?program :hasProgramName     ?programName ;
             :hasProgramDuration ?duration .
}
ORDER BY ?dept ?programName"""
    },
    {
        "id": 14,
        "question": "Which core courses are in the BSc (Hons) in IT program?",
        "sparql": PREFIX + """
SELECT ?courseCode ?courseName ?credits
WHERE {
    ?program :hasProgramName "Bsc (Hons) in IT" ;
             :containCourses  ?course .
    ?course  :hasCourseCode ?courseCode ;
             :hasCourseName  ?courseName ;
             :hasNumberOfCredits ?credits ;
             :hasCourseType  "Core" .
}
ORDER BY ?courseCode"""
    },
    {
        "id": 15,
        "question": "Which students are postgraduate and who advises them?",
        "sparql": PREFIX + """
SELECT ?studentName ?regNo ?advisorName
WHERE {
    ?student a :PostgraduateStudent ;
             :hasPersonName ?studentName ;
             :hasRegistrationNumber ?regNo ;
             :hasAdvisor ?advisor .
    ?advisor :hasPersonName ?advisorName .
}"""
    },
    {
        "id": 16,
        "question": "How many courses does each department offer?",
        "sparql": PREFIX + """
SELECT ?dept (COUNT(?course) AS ?numCourses)
WHERE {
    ?dept a :Department ;
          :offersCourse ?course .
}
GROUP BY ?dept
ORDER BY DESC(?numCourses)"""
    },
    {
        "id": 17,
        "question": "Which courses have 3 or more credits?",
        "sparql": PREFIX + """
SELECT ?courseCode ?courseName ?credits ?courseType
WHERE {
    ?course a :Course ;
            :hasCourseCode ?courseCode ;
            :hasCourseName ?courseName ;
            :hasNumberOfCredits ?credits ;
            :hasCourseType ?courseType .
    FILTER(?credits >= 3.0)
}
ORDER BY DESC(?credits) ?courseCode"""
    },
    {
        "id": 18,
        "question": "What courses does the Department of Computational Mathematics offer?",
        "sparql": PREFIX + """
SELECT ?courseCode ?courseName ?credits ?courseType
WHERE {
    :Department_of_Computational_Mathematics :offersCourse ?course .
    ?course :hasCourseCode ?courseCode ;
            :hasCourseName ?courseName ;
            :hasNumberOfCredits ?credits ;
            :hasCourseType ?courseType .
}
ORDER BY ?courseType ?courseCode"""
    },
    {
        "id": 19,
        "question": "List all persons (staff and students) in each department.",
        "sparql": PREFIX + """
SELECT ?dept ?personName ?email
WHERE {
    ?dept   a :Department .
    ?person :isMemberOf ?dept ;
            :hasPersonName ?personName ;
            :hasEmail      ?email .
}
ORDER BY ?dept ?personName"""
    },
    {
        "id": 20,
        "question": "How many courses does each academic staff member teach?",
        "sparql": PREFIX + """
SELECT ?staffName ?position (COUNT(?course) AS ?numCourses)
WHERE {
    ?staff a :AcademicStaff ;
           :hasPersonName ?staffName ;
           :hasPosition   ?position .
    OPTIONAL {
        ?staff :teaches ?course .
    }
}
GROUP BY ?staff ?staffName ?position
ORDER BY DESC(?numCourses)
"""
    },
]


# ── Helper ─────────────────────────────────────────────────────
def run_sparql(sparql, label):
    try:
        results = g.query(sparql)
        columns = [str(v) for v in results.vars]
        rows = []
        for row in results:
            rows.append({
                col: (str(row[col]) if row[col] is not None else "—")
                for col in columns
            })
        return jsonify({"label": label, "columns": columns,
                        "rows": rows, "count": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Routes ─────────────────────────────────────────────────────
@app.route("/api/questions")
def get_questions():
    return jsonify([{"id": q["id"], "question": q["question"]}
                    for q in QUESTIONS])


@app.route("/api/query/<int:qid>")
def run_question(qid):
    cq = next((q for q in QUESTIONS if q["id"] == qid), None)
    if not cq:
        return jsonify({"error": "Not found"}), 404
    return run_sparql(cq["sparql"], cq["question"])

@app.route("/api/sparql/<int:qid>")
async def get_sparql(qid):
    sp = next((q for q in QUESTIONS if q['id'] == qid), None)
    if not sp:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"sparql": sp["sparql"]})


@app.route("/api/custom", methods=["POST"])
def run_custom():
    data = request.get_json()
    if not data or "sparql" not in data:
        return jsonify({"error": "No SPARQL provided"}), 400
    sparql = PREFIX + "\n" + data["sparql"]
    return run_sparql(sparql, "Custom Query")


@app.route("/api/stats")
def stats():
    q = PREFIX + """
    SELECT (COUNT(DISTINCT ?course) AS ?courses)
           (COUNT(DISTINCT ?program) AS ?programs)
           (COUNT(DISTINCT ?dept) AS ?departments)
           (COUNT(DISTINCT ?staff) AS ?staff)
           (COUNT(DISTINCT ?student) AS ?students)
    WHERE {
        { ?course rdf:type/rdfs:subClassOf* :Course . }
        UNION
        { ?program rdf:type/rdfs:subClassOf* :Program . }
        UNION
        { ?dept rdf:type/rdfs:subClassOf* :Department . }
        UNION
        { ?staff rdf:type/rdfs:subClassOf* :AcademicStaff . }
        UNION
        { ?student rdf:type/rdfs:subClassOf* :Student . }
    }"""
    try:
        results = g.query(q)
        row = list(results)[0]
        return jsonify({
            "triples": len(g),
            "courses": int(row.courses),
            "programs": int(row.programs),
            "departments": int(row.departments),
            "staff": int(row.staff),
            "students": int(row.students),
        })
    except Exception as e:
        print(f"Stats Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)