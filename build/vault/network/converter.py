import os.path
import os
import json

data_path = '../../../fixBreaks'


if __name__ == '__main__':
    all_tests = [x[0] for x in os.walk(os.path.join(os.path.dirname(__file__), data_path))][1:]
    print (all_tests)
    for select in all_tests:
        print(select)
        test_file = os.path.join( select, 'test')
        test_file += ".json"
        with open(test_file) as datafile:
            data = json.loads( datafile.read())
            programs = data['programs']
            oracle_arguments = data['arguments']['argv']
            oracle_programs = []
            for program in programs:
                program_data = program['program']
                oracle_programs.append(program_data)
            oracle_file = os.path.join( select, 'oracle')
            oracle_file += '.json'
            with open(oracle_file, 'w') as oracle:
                data['programs'] = oracle_programs
                data['arguments'] = oracle_arguments
                oracle.write(json.dumps(data))




