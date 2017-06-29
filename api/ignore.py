import os


def get_python_files():
    return ' '.join(filter(
        lambda x: x.endswith('.py') and
        not any(y in x for y in ['ipython',
                                 'get_data_parallel']),
        os.listdir('.')))


if __name__ == '__main__':
    print(' '.join(
          map(lambda y: '--ignore ' + y,
              filter(lambda x: '.py' not in x or
                     any(y in x for y in ['ipython',
                                          'get_data_parallel']),
                     os.listdir('.')))))
