http://ubaumann.github.io/naf_workshop_cli_tool/

the guy has no microphone
wifi never works

material: https://github.com/ubaumann/mtu_tool
Look at the different branches (also downloaded locally)

## Poetry
- manage all dependencies more easily
basic usage here: https://python-poetry.org/docs/basic-usage/

lab: https://ubaumann.github.io/naf_workshop_cli_tool/lab_poetry/#setup-a-new-project-and-add-dependencies-and-development-dependencies 


Create a new project with Poetry. Our example use case is a small MTU tool.
Add dependencies to the project:
- rich
- nornir
- nornir-napalm
- typer

Add development dependencies
 - pytest
 - black

Install the created project
Open a shell with loaded virtual environment
Display outdated packages

```
[solution]
poetry new mtu-tool
cd mtu-tool
poetry add rich nornir nornir-napalm typer
poetry add --group=dev pytest black
poetry install
poetry shell
poetry show --outdated
```


## Nornir
https://ubaumann.github.io/naf_workshop_cli_tool/nornir/

repo: https://github.com/ubaumann/mtu_tool
check branch: nornir
cloned here:  /c/Users/tongb/Desktop/WS_CLI/mtu_tool

Pretty poor demo.. showing random code?
Nornir plugins: https://nornir.tech/nornir/plugins/

### interesting things
. in the inventory connection_options he uses a napalm mocked date
  which means that there is no device and no real connection
  the data is taked from a  file
  ```
  r01:
  hostname: 192.168.121.101
  groups:
    - eos
    - edge1
  connection_options:
    napalm:
      extras:
        optional_args:
          path: mocked_napalm_data/r01
  ```

. the way he strutures the app is as follow:
  . create a nornir instance  `nr = init_nornir()`
    Note that thi is a function in the repo inside the helpers.py
  . call a function passing the nornir instance
    e.g. `data, result = interfaces(nr)`

  the function in this case is as follows:  

```
def interfaces(nr: Nornir,hostname: Optional[str] = None,
                ) -> Tuple[Dict["str", List[InterfaceItem]], AggregatedResult]:
    """Collect the mtu for all interfaces"""

    if hostname:
        nr = nr.filter(name=hostname)
        if len(nr.inventory) == 0:
            raise NoHostFoundException(f"Host {hostname} not found in inventory")

    result = nr.run(
        task=napalm_get,  
        getters=[
            "get_interfaces",
        ],
    )

    data = {}
    for host, mulit_result in result.items():
        data_interface = []
        interfaces = mulit_result[0].result.get("get_interfaces", {})
        for int_name, int_data in interfaces.items():
            data_interface.append(InterfaceItem(name=int_name, mtu=int_data.get("mtu")))
        data[host] = data_interface

    return data, result
```   
  . napalm_get is more or less explained here:
  https://nornir.tech/nornir_napalm/html/api/tasks.html#nornir_napalm.plugins.tasks.napalm_get
    above it gets interfaces but you can **get** different things, for instance
    in the `neighbors.py` function it is used to get lldp_neighbors
    ```
    result_lldp = nr_host.run(
        task=napalm_get,
        getters=[
            "get_lldp_neighbors",
        ],
    )
    ```
   
    . a useful option when using nornir is to run a function only to a subset of hosts using the filter function before runnint a task:
    ```
    hosts = ['R1', 'R2', ..., 'Rn']
    result_interfaces = nr.filter(F(name__any=hosts)).run(
        task=napalm_get,
        getters=[
            "get_interfaces",
        ],
    )
    ```
    in the snippet above, taken from the `neighbors.py` nornir branch we run the task but only on the hosts that satisfy the fitler object F(..)
    this filter can check many things e.g.
      - if the list of groups for a host contain a specific word
        `F(groups__contains="word")`
      - single hostname filter don't require fitler objects: 
        `nr_host = nr.filter(name=hostname)`  
      - the Object F can be used for negative filter
        `~F(..)`
      -  
    from the object returned by the filter, you can get the inventory hosts:
    ```filtered_inventory = nr.filter(F()..))
       filtered_inventory.inventory.hosts
    ```
      - filters can be composed inside the `nr.filter()` function
        nr.filter(F(..) | F(..))
    Examples on filters are available here: 
     - https://nornir.readthedocs.io/en/latest/howto/advanced_filtering.html 
     - https://nornir.readthedocs.io/en/latest/howto/filtering_deep_dive.html#Tutorial-Inventory 


 . in the last function: `path.py`   
   we use tasks and aggregated results 
   but it's not very clear how it is used.. it seems something like this: 

   https://nornir.readthedocs.io/en/latest/tutorial/task_results.html 

   **AggregatedResult.** This object is a dict-like object you can use to iterate over or access hosts directly.
   Inside each host result (the key looks like `<host>.<task>`) you then have a multi result object which is like a list.. so for every host and task you can access the potentially different results 
   e.g. `result["<host>.<task>"][0].changed` or `result["host2.cmh"][0].failed`

   Another intereseting things is using a single function (task) to run multiple activities.. basically we get as input the Task object and then we run both a napalm_cli and then a napalm_get
   ```
   def get_next_hop(task: Task, destination: IPv4Interface) -> Result:
    if cached := CACHE.get(task.host.name):
        return cached

    show_cmd = f"show ip route {destination} | json"
    result_cli = task.run(
        task=napalm_cli,
        commands=[show_cmd],
        severity_level=logging.DEBUG,
    )
    result_getters = task.run(
        task=napalm_get,
        getters=[
            "get_lldp_neighbors",
            "get_interfaces",
        ],
        severity_level=logging.DEBUG,
    )

   [...] 
   ```
   The task then continues..

   The way the task is called is as follows:
   ```
     result = nr_host.run(
            task=get_next_hop,
            destination=destination,
        )
   ```
   Note that bth result_cli and result_getters give access to their result
   under `result_cli[0].result[show_cmd]` or `result_getters[0].result[<get_command>]`


Nornir provides the task object that gives access to the host of the inventory etc..
it can also give you access to the way nornir is configured (e.g. task.nornir.config)
you can also set the task severity level when use the run( ... ) commands
`e.g. run(... , severity_level=logging.INFO)`

## RICH OUTPUT
you can call rich during a breakout from python DEBUG
breakout()

at the command prompt type
`from rich import inspect`
now that will help showing the objects during the debug session

rich also integrtes with nornir
```
from nornir_rich.functions import print_result

results = nr.run(
    task=hello_world
)

print_result(results)
print_result(results, vars=["diff", "result", "name", "exception", "severity_level"])
```


it can also be used to generate a progress branch
```
from time import sleep
from nornir_rich.progress_bar import RichProgressBar


def random_sleep(task: Task) -> Result:
    delay = randrange(10)
    sleep(delay)
    return Result(host=task.host, result=f"{delay} seconds delay")


nr_with_processors = nr.with_processors([RichProgressBar()])
result = nr_with_processors.run(task=random_sleep)
```

The examples for Rich presentations are in
C:\Users\tongb\Desktop\WS_CLI\mtu_tool
branch:  remotes/origin/rich

```
[beautify interfaces.py]

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def print_interfaces(
    data: Dict["str", List[InterfaceItem]],
    min_mtu: Optional[int] = None,
    console: Console = Console(),
) -> None:


    for host, interface_list in data.items():
        table = Table(style="cyan", row_styles=["green"], expand=True)
        table.add_column("Interface Name")
        table.add_column("MTU", justify="right")

        for item in interface_list:
            table.add_row(item.name, _mtu_rich_str(mtu=item.mtu, min_mtu=min_mtu))

        title_colour = (
            "red"
            if min_mtu and min([x.mtu for x in interface_list]) < min_mtu
            else "green"
        )
        console.print(
            Panel(table, title=f"[{title_colour}]Device [b]{host}[/b]", style="magenta")
        )


```
This function will print a table for each router with interfces and mtu
Basically you create a table, you populate it and print the resul to a console


## Textual TUI
it is used for textual user interfaces
it gives emoji and expandable 



# Pydantic
Dataclasses are ok but sometimes you want to have real model and validation for your data.
You use it to validate the data you get back (e.g. via json or any API) and be struturesit is 
conforming to the model you want.
The new version of pydantic is written in rust so speed of validation should not be a problem.

`datamodel-code-generator` Pydantic models can be geenrated from JSON Schema and other formats
This schema generation is mostly useful if you want to create api yourself and provide schema to other teams
another use case is if you need to interact with YANG models



# Typer
Built on top of click and used to build our cli tool
see https://pravash-techie.medium.com/python-better-clis-with-typer-a8783fafec6c
for details

Check also branch cli_tool, file cli_tool/mtu_tool/main.py 

Note that typer support rich so you can have rich text as help..

https://typer.tiangolo.com/

## Simple app
```
import typer

app = typer.Typer()

@app.command()
def command1():
    print("hello world")

@app.command()
def command2(name):
    print(f"hello {name}")

if __name__ == "__main__":
    app()
```
This creates an app with 2 commands;  
you would call it with the program name followed by the `<command>` and, 
in case of the second one, an additional parameter

you can use Typer to give help on the arguments if you specify them during
the function definition
```
@app.command()
def greet2(name: str = typer.Argument("world",help="The name to greet", 
                                       show_default=True),
          force: bool = False):
    <function code>
```
above you are goin to have full help on the name parameter and partial help for boolean force parameter

you can also ask Typer to ask a paramter if it is not provided

you can run validation on the parameter on the parameter before executing the actual code
via the `callback` function marked by a decorator (but not sure if you can tie it to a specific command)

you can also define sub apps that have a nested context (help, execution, etc..)

In the lab repo file: `cli_tool/mtu_tool/main.py`, note the different options for typer args to enhance the help:


# check OPsmill infrahub
https://www.opsmill.com/
Jake and GR use it a lot and love it