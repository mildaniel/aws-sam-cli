"""
Common CLI options shared by various commands
"""

import click


def stack_name_click_option():
    return click.option(
        "--stack-name",
        help=(
            "Name of corresponding deployed stack.(Not including "
            "a stack name will only show local resources defined "
            "in the template.) "
        ),
        type=click.STRING,
    )


def stack_name_option(f):
    return stack_name_click_option()(f)


def output_click_option():
    return click.option(
        "--output",
        default="table",
        help="Output the results from the command in a given " "output format (json or table). ",
        type=click.Choice(["json", "table"], case_sensitive=False),
    )


def output_option(f):
    return output_click_option()(f)


def query_click_option():
    return click.option(
        "--query",
        help="Query the resultant JSON string using JMESPath JSON query language.",
        type=click.STRING,
    )


def query_option(f):
    return query_click_option()(f)


def list_common_options(f):
    f = output_option(f)
    f = query_option(f)
    return f


STACK_NAME_WARNING_MESSAGE = (
    "The --stack-name options was not provided, displaying only local template data. "
    "To see data about deployed resources, provide the corresponding stack name."
)


def stack_name_not_provided_message():
    click.secho(
        fg="yellow",
        message=STACK_NAME_WARNING_MESSAGE,
        err=True,
    )
