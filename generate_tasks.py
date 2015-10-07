"""Use this script to generate tasks via hyperparameter search. This is a first pass, but eventually
something similar to this will be added to the mri.server. Also worth noting is that this may be spun off into
a separate module if it's useful enough

To use, first copy the configuration example to `config` and add your own values. The mother model and solver
should simply replace any fields to be replaced by %{field-name}%. Then, create the hyperparameter file:

field-name: 1,2,3,4
field-name2: 0.23, 1.2, 5.4

The field names can be in either the model or solver, just use unique names

To run script:

python generate_tasks random -n 5       # Generates 5 random tasks sampled from the hyperparameter distribution
python generate_tasks grid              # Generate tasks for all possible hyperparameter values
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import configparser
import os
import re
import uuid
import random
import json
import argparse
import itertools


def create_dir(path):
    """Helper to create dir if one doesn't exist"""
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


class TaskCreator(object):
    def __init__(self, config_file):
        """New TaskCreator with given config file

        Arguments
        ----------
        config_file : string
            filename of configuration file
        """
        # Get config information
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.folder = self.config.get('generate-tasks', 'task_folder')
        self.hyperparams = self.config.get('generate-tasks', 'hyperparams')

        model = self.config.get('generate-tasks', 'mother_model')
        solver = self.config.get('generate-tasks', 'mother_solver')

        # Read in mother files
        with open(model) as m:
            self.model = str(m.read())
        with open(solver) as s:
            self.solver = str(s.read())

        self._verify()

    def _verify(self):
        """Verify that this TaskCreator is valid, i.e. that our parameters match up, etc"""
        def remove_chars(new_str):
            to_remove = "{}%"
            for char in to_remove:
                new_str = new_str.replace(char, '')
            return new_str

        # Find all of the things we need to replace
        tag_reg = re.compile(r'\%\{.+\}\%')
        model_matches = [remove_chars(c) for c in re.findall(tag_reg, self.model)]
        solver_matches = [remove_chars(c) for c in re.findall(tag_reg, self.solver)]
        to_replace = set(model_matches).union(set(solver_matches))
        # Find all of the things we are replacing with
        params = []
        with open(self.hyperparams) as f:
            for line in f:
                task, items = line.split(':')
                params.append(task)
        for_replace = set(params)
        if to_replace != for_replace:
            print('Error! There is a mismatch between template files and replacement parameters')
            print('Tempate files must replace {0}'.format(to_replace))
            print('but the hyperparameter file is trying to replace {0}'.format(for_replace))
            raise Exception('Input configuration mismatch')

    def sample_random(self):
        """Sample a random permutation of hyperparameters

        Arguments
        ----------
        None
        """
        sample_dict = {}
        with open(self.hyperparams) as f:
            for line in f:
                task, items = line.split(':')
                params = [item.strip() for item in items.split(',')]
                sample_dict[task] = random.choice(params)
        return sample_dict

    def sample_one(self):
        """Sample a single permutation of hyperparameters but don't repeat

        Arguments
        ----------
        None
        """
        sample_dict = {}
        with open(self.hyperparams) as f:
            for line in f:
                task, items = line.split(':')
                sample_dict[task] = [item.strip() for item in items.split(',')]
            keys = sample_dict.keys()
            values = list(itertools.product(*sample_dict.values()))
            all_dicts = [dict(zip(keys, v)) for v in values]
            for d in all_dicts:
                yield d

    def create_task(self, **kwargs):
        """Create a task from random search with the given kwargs

        Arguments
        ----------
        kwargs : dict
            Replacements to make in model and solver template files

        Returns
        ----------
        task_path : string
            Name and path of this task
        """
        # Setup the directory structure if it doesn't exist
        create_dir(self.folder)
        task_name = str(uuid.uuid4())
        # Create the new task
        folder_repr = str(kwargs).replace(':', '-')
        folder_repr = folder_repr.replace('u\'', '')
        folder_repr = folder_repr.replace('\'', '')
        task_path = os.path.join(self.folder, folder_repr)
        create_dir(task_path)
        snapshot_path = os.path.join(task_path, 'snapshots')
        create_dir(snapshot_path)
        model_location = os.path.join(task_path, 'model.prototxt')
        solver_location = os.path.join(task_path, 'solver.prototxt')
        # Create a new model and solver
        new_model = self.model
        new_solver = self.solver
        for key in kwargs:
            search_str = '%{{{0}}}%'.format(key)
            new_model = new_model.replace(search_str, kwargs[key])
            new_solver = new_solver.replace(search_str, kwargs[key])
        # Replace net and snapshot_prefix in solver
        snapshot_prefix = '\"{}\"'.format(os.path.join(snapshot_path, 'snapshots'))
        net = '\"{}\"'.format(model_location)

        new_solver = self.replace_solver_param(new_solver, 'net', net)
        new_solver = self.replace_solver_param(new_solver, 'snapshot_prefix', snapshot_prefix)
        # Write files
        with open(model_location, 'w') as f:
            f.write(new_model)
        with open(solver_location, 'w') as f:
            f.write(new_solver)
        # Create task file
        train_directive = [{'type': 'train', 'parameters': {'solver': solver_location}}]
        task_file = {'directives': train_directive, 'title': str(kwargs), 'id': task_name}
        with open(os.path.join(task_path, 'task.json'), 'w') as f:
            json.dump(task_file, f, indent=4)
        return task_path

    @staticmethod
    def replace_solver_param(solver, param, new_val):
        """Replace a parameter from the solver of this task.

        Note: We should probably use a similar method so the user doesn't have to make a special
        solver and model template, but for now we'll just use this for the net and snapshot_prefix
        parts of the solver file.

        Arguments
        ----------
        param : string
            Name of the parameter to replace

        new_val : string
            Replacement value

        Returns
        ----------
        replaced_solver : string
            A copy of the solver file but with the replacement made
        """
        replaced_solver = ""
        for line in solver.splitlines():
            new_line = line
            if ':' in line:
                p, value = line.split(':')
                if p == param:
                    new_line = '{0}: {1}'.format(param, new_val)
            replaced_solver += new_line + os.linesep
        return replaced_solver


def main():
    parser = argparse.ArgumentParser(description='Create tasks for mri')
    parser.add_argument('search_type')
    parser.add_argument('-n')
    parser.add_argument('--config', default='config.txt')
    arg = parser.parse_args()

    task = TaskCreator(arg.config)
    task_list = os.path.join(task.folder, 'generated_tasks.txt')
    task_dir = os.path.dirname(task_list)
    create_dir(task_dir)

    if arg.search_type == 'grid':
        with open(task_list, 'w') as f:
            for samp in task.sample_one():
                task_path = task.create_task(**samp)
                full_path = os.path.join(task_path, 'task.json')
                f.write(full_path)
                f.write(os.linesep)
    elif arg.search_type == 'random':
        n_samps = int(arg.n)
        with open(task_list, 'w') as f:
            for n in range(n_samps):
                samp = task.sample_random()
                task_path = task.create_task(**samp)
                full_path = os.path.join(task_path, 'task.json')
                f.write(full_path)
                f.write(os.linesep)
    else:
        print('Invalid search type, specify either \'grid\' or \'random\'')
        return

if __name__ == "__main__":
    main()
