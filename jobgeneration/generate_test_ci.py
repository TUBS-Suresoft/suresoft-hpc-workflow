from jinja2 import Template
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEST_CI_TEMPLATE = TEMPLATES_DIR / "tests-ci.yml.j2"
GENERATED_DIR = Path("generated")
TEST_CI_FILE = GENERATED_DIR / "tests-ci.yml"
TEST_FILE_DIR = Path("tests")


def build_regression_job_string(tests: list[str]) -> str:
    template = Template(TEST_CI_TEMPLATE.read_text())
    return template.render(test_cases=tests)


def main():
    tests_files = [item.stem for item in TEST_FILE_DIR.glob("*-test")]
    tests_ci_file = build_regression_job_string(tests_files)
    TEST_CI_FILE.write_text(tests_ci_file)

if __name__ == "__main__":
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    main()