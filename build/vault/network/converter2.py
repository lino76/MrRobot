import os.path
import os
import json

data_path = '../../../fixBreaks'


if __name__ == '__main__':
    all_tests = [x[0] for x in os.walk(os.path.join(os.path.dirname(__file__), data_path))][1:]
   # print (all_tests)
    for select in all_tests:
        #print(select)
        test_file = os.path.join(select, 'test')
        test_file += ".json"
        resp_file = os.path.join(select, 'oracle_resp')
        resp_file += ".json"
        with open(test_file) as datafile, open(resp_file) as respfile:
            data = json.loads(datafile.read())
            resp = json.loads(respfile.read())
            programs = data['programs']
            output = resp['output']
            #print(output)
            res = map(lambda x, y: x.update({'output' : y}), programs, output)
            print(list(res))
            data['programs'] = programs
            oracle_file = os.path.join(select, 'full_test')
            oracle_file += '.json'
            with open(oracle_file, 'w') as oracle:
                oracle.write(json.dumps(data))




