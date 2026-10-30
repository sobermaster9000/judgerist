import subprocess
import io

n_tests = 0
with open('n_tests', 'r') as f:
    n_tests = int(f.read().strip())

if n_tests == 0:
    print('could not read content of n_tests')
    exit(1)

ac_count = 0
wa_count = 0
tle_count = 0
me_count = 0
re_count = 0

for test_i in range(n_tests):
    print(f'== test {test_i} ==')

    _in = ''
    _out = ''

    _test_out = None
    _test_err = None

    try:
        with open(f'{test_i}_in', 'r') as f:
            _in = f.read()
        with open(f'{test_i}_out', 'r') as f:
            _out = f.read()

        _test_out = open(f'_{test_i}_out', 'w+')
        _test_err = open(f'_{test_i}_err', 'w+')

        result = None

        with open(f'{test_i}_in', 'r') as test_in:
            result = subprocess.run(['python3', 'submission.py'], stdin=test_in, stdout=_test_out, stderr=_test_err, timeout=1, text=True)

        _test_out.seek(0)

        with open(f'{test_i}_out', 'r') as test_out:
            print('-- in -- ')
            print(_in.strip(), end='\n\n')
            print('-- out --')
            print(_out.strip(), end='\n\n')
            print('-- sub out --')
            print(_test_out.read().strip(), end='\n\n')

            _test_out.seek(0)

            is_ac = _test_out.read().strip() == test_out.read().strip()
            ac_count += is_ac
            print('verdict:', ('WA', 'AC')[is_ac], end='\n\n')

    except subprocess.TimeoutExpired:
        tle_count += 1
        print('TLE', end='\n\n')

    except Exception as e:
        re_count += 1
        print('RE')
        print(e, end='\n\n')

    finally:
        if isinstance(_test_out, io.IOBase) and not _test_out.closed:
            _test_out.close()
        if isinstance(_test_err, io.IOBase) and not _test_err.closed:
            _test_err.close()

print('== final verdict ==')

if ac_count == n_tests:
    print('AC')
elif wa_count:
    print('WA')
elif tle_count:
    print('TLE')
elif me_count:
    print('ME')
elif re_count:
    print('RE')

# resources library for subprocess memory
# restricted bash to restrict to dir
