import os
from pathlib import Path
from visivo.commands.init import init
from visivo.models.target import TypeEnum
from tests.support.utils import temp_folder
from click.testing import CliRunner

runner = CliRunner()


def test_init_with_sqlite():
    if os.environ.get("CI"):
        return
    tmp = temp_folder()

    response = runner.invoke(init, input=f"{tmp}\nsqlite\n")
    assert f"Created project in '{tmp}'" in response.output
    assert response.exit_code == 0
    assert Path(f"{tmp}/.env").read_text() == "DB_PASSWORD=EXAMPLE_password_l0cation"
    assert Path(f"{tmp}/.gitignore").read_text() == ".env"
    assert os.path.exists(f"{tmp}/visivo_project.yml")
    assert os.path.exists(f"{tmp}/local.db")


def test_init_with_postgres():
    if os.environ.get("CI"):
        return
    tmp = temp_folder()

    response = runner.invoke(
        init,
        input=f"{tmp}\n"
        + "postgresql\n"
        + "database\n"
        + "username\n"
        + "password\n"
        + "password\n",
    )
    assert f"Created project in '{tmp}'" in response.output
    assert response.exit_code == 0
    assert Path(f"{tmp}/.env").read_text() == "DB_PASSWORD=password"
    assert Path(f"{tmp}/.gitignore").read_text() == ".env"
    assert os.path.exists(f"{tmp}/visivo_project.yml")