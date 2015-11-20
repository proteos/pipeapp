# Useful App templates for creating basic and pipeline apps.

## BasicApp
To create a basic app, subclass `.lib.BasicApp` class. The app object can be instantiated either using commandline
arguments (see `run_from_console()` of the `example.py` for an example) or using a kwargs dictionary containing 
essential data. (The latter is useful for writing tests: instead of struggling with command line and parsing outputs,
one can instantiate an app with a dictionary and interrogate the app object directly.)

Creating an app in such manner instantly provides benefits like automatically creating the workdir, 
setting up logging easily, etc.
One more important feature is hook methods init(), run(), exit(). One can put all the initialization code in the init(),
main logic flow in the run(), and all the exit/cleanup code in the exit() method. They will run consecutively.

## PipelineApp
Another app class is `PipelineApp`. Besides the benefits of the `BasicApp`, this class automatically creates several 
directories inside the workdir: `in`, `out`, `log`, `tmp`.
All these directories can be accessed by instance variables `self.dir_*`.
I found it useful to use this structure for all my pipelina apps.
The `in` directory can be used for all the input files that were not produced 
by your app e.g. downloaded input files, symlinks, etc.
The `out` contains all the final output files.
The `log` contains the main log file (which is created automatically) and all the other log files.
The `tmp` directory is meant for all the temporary files. I put all the files in it, even the files that are meant to be
final outputs. When all the computation is done, I move them to `out` using `.lib.shell:move_files()`.
This is better than creating these files directly in `out` because if the app fails you will not know whether the output
files are good or corrupt, whereas first putting them in `tmp` and only moving them after all the business logic is done 
guarantees that anything that is in `out` is good. This is because file move is an atomic operation.

There are quite a few useful functions in `shell.py` for shell and file operations.
