import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__));
new_file_path = str(os.path.join(dir_path, 'data.csv'));

df = pd.read_csv(new_file_path);

def univariateKarma():
    np.log10(df[['Comment Karma', 'Post Karma', 'Total Karma']]).plot.kde();
    plt.title(f'Distribution of log10(Karma)')
    plt.xlabel(f'log10(Karma)')
    plt.ylabel('Density')
    plt.show()

def univariateYears():
    df.groupby('Creation')['Username'].count().plot(kind='bar');
    plt.title('Distribution of accounts by creation year');
    plt.xlabel('Year');
    plt.ylabel('Count');
    plt.show();

def yearKarma():
    df.groupby('Creation')[['Comment Karma', 'Post Karma', 'Total Karma']].mean().plot(kind='bar');
    plt.title(f'Average Karma of accounts per year');
    plt.xlabel('Year');
    plt.ylabel(f'Average Karma');
    plt.show();

univariateYears();