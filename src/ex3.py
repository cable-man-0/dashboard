import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
from sklearn.preprocessing import StandardScaler
from joblib import dump
from tqdm import tqdm
import warnings

warnings.filterwarnings('ignore')

DATASET_DIRECTORY = './dataset/CICIoT2023/'
X_COLUMNS = ['flow_duration', 'Header_Length', 'Protocol Type', 'Duration', 'Rate', 'Srate', 'Drate', 'fin_flag_number',
             'syn_flag_number', 'rst_flag_number', 'psh_flag_number', 'ack_flag_number', 'ece_flag_number',
             'cwr_flag_number', 'ack_count', 'syn_count', 'fin_count', 'urg_count', 'rst_count', 'HTTP', 'HTTPS',
             'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP', 'UDP', 'DHCP', 'ARP', 'ICMP', 'IPv', 'LLC', 'Tot sum',
             'Min', 'Max', 'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Magnitue', 'Radius', 'Covariance', 'Variance',
             'Weight']
Y_COLUMN = 'label'


def load_datasets(directory, split_ratio=0.8):
    datasets = [k for k in os.listdir(directory) if k.endswith('.csv')]
    datasets.sort()
    training_sets = datasets[:int(len(datasets) * split_ratio)]
    test_sets = datasets[int(len(datasets) * split_ratio):]
    return training_sets, test_sets


def train_and_evaluate_models(training_sets, test_sets, model_cls, model_name, label_mapping=None):
    scaler = StandardScaler()
    ML_models = [model_cls(n_estimators=100)]

    preds = {i: [] for i in range(len(ML_models))}
    y_test = []

    for train_set in tqdm(training_sets):
        d_train = pd.read_csv(os.path.join(DATASET_DIRECTORY, train_set))
        d_train[X_COLUMNS] = scaler.fit_transform(d_train[X_COLUMNS])
        if label_mapping:
            d_train[Y_COLUMN] = [label_mapping[k] for k in d_train[Y_COLUMN]]
        for model in ML_models:
            model.fit(d_train[X_COLUMNS], d_train[Y_COLUMN])

    for test_set in tqdm(test_sets):
        d_test = pd.read_csv(os.path.join(DATASET_DIRECTORY, test_set))
        d_test[X_COLUMNS] = scaler.transform(d_test[X_COLUMNS])
        if label_mapping:
            d_test[Y_COLUMN] = [label_mapping[k] for k in d_test[Y_COLUMN]]
        y_test += list(d_test[Y_COLUMN].values)
        for i, model in enumerate(ML_models):
            y_pred = list(model.predict(d_test[X_COLUMNS]))
            preds[i] = preds[i] + y_pred

    for k, v in preds.items():
        y_pred = v
        print(f"##### {model_name[k]} #####")
        print('accuracy_score: ', accuracy_score(y_pred, y_test))
        print('recall_score: ', recall_score(y_pred, y_test, average='macro'))
        print('precision_score: ', precision_score(y_pred, y_test, average='macro'))
        print('f1_score: ', f1_score(y_pred, y_test, average='macro'))
        print()
        print()
        print()

    return ML_models


def export_models(models, model_names, file_paths):
    for model, file_path in zip(models, file_paths):
        dump(model, file_path)


if __name__ == "__main__":
    training_sets, test_sets = load_datasets(DATASET_DIRECTORY)

    # Classification: 34 (33+1) classes
    model_34_classes = train_and_evaluate_models(training_sets, test_sets, RandomForestClassifier,
                                                  ["RandomForestClassifier (34 classes)"])

    # Classification: 8 (7+1) classes
    dict_7classes = {}
    dict_7classes['DDoS-RSTFINFlood'] = 'DDoS'
    dict_7classes['DDoS-PSHACK_Flood'] = 'DDoS'
    dict_7classes['DDoS-SYN_Flood'] = 'DDoS'
    dict_7classes['DDoS-UDP_Flood'] = 'DDoS'
    dict_7classes['DDoS-TCP_Flood'] = 'DDoS'
    dict_7classes['DDoS-ICMP_Flood'] = 'DDoS'
    dict_7classes['DDoS-SynonymousIP_Flood'] = 'DDoS'
    dict_7classes['DDoS-ACK_Fragmentation'] = 'DDoS'
    dict_7classes['DDoS-UDP_Fragmentation'] = 'DDoS'
    dict_7classes['DDoS-ICMP_Fragmentation'] = 'DDoS'
    dict_7classes['DDoS-SlowLoris'] = 'DDoS'
    dict_7classes['DDoS-HTTP_Flood'] = 'DDoS'

    dict_7classes['DoS-UDP_Flood'] = 'DoS'
    dict_7classes['DoS-SYN_Flood'] = 'DoS'
    dict_7classes['DoS-TCP_Flood'] = 'DoS'
    dict_7classes['DoS-HTTP_Flood'] = 'DoS'


    dict_7classes['Mirai-greeth_flood'] = 'Mirai'
    dict_7classes['Mirai-greip_flood'] = 'Mirai'
    dict_7classes['Mirai-udpplain'] = 'Mirai'

    dict_7classes['Recon-PingSweep'] = 'Recon'
    dict_7classes['Recon-OSScan'] = 'Recon'
    dict_7classes['Recon-PortScan'] = 'Recon'
    dict_7classes['VulnerabilityScan'] = 'Recon'
    dict_7classes['Recon-HostDiscovery'] = 'Recon'

    dict_7classes['DNS_Spoofing'] = 'Spoofing'
    dict_7classes['MITM-ArpSpoofing'] = 'Spoofing'

    dict_7classes['BenignTraffic'] = 'Benign'

    dict_7classes['BrowserHijacking'] = 'Web'
    dict_7classes['Backdoor_Malware'] = 'Web'
    dict_7classes['XSS'] = 'Web'
    dict_7classes['Uploading_Attack'] = 'Web'
    dict_7classes['SqlInjection'] = 'Web'
    dict_7classes['CommandInjection'] = 'Web'

    dict_7classes['DictionaryBruteForce'] = 'BruteForce'
    model_8_classes = train_and_evaluate_models(training_sets, test_sets, RandomForestClassifier,
                                                 ["RandomForestClassifier (8 classes)"], dict_7classes)

        # Classification: 2 (1+1) classes
    dict_2classes = {}
    dict_2classes['DDoS-RSTFINFlood'] = 'Attack'
    dict_2classes['DDoS-PSHACK_Flood'] = 'Attack'
    dict_2classes['DDoS-SYN_Flood'] = 'Attack'
    dict_2classes['DDoS-UDP_Flood'] = 'Attack'
    dict_2classes['DDoS-TCP_Flood'] = 'Attack'
    dict_2classes['DDoS-ICMP_Flood'] = 'Attack'
    dict_2classes['DDoS-SynonymousIP_Flood'] = 'Attack'
    dict_2classes['DDoS-ACK_Fragmentation'] = 'Attack'
    dict_2classes['DDoS-UDP_Fragmentation'] = 'Attack'
    dict_2classes['DDoS-ICMP_Fragmentation'] = 'Attack'
    dict_2classes['DDoS-SlowLoris'] = 'Attack'
    dict_2classes['DDoS-HTTP_Flood'] = 'Attack'

    dict_2classes['DoS-UDP_Flood'] = 'Attack'
    dict_2classes['DoS-SYN_Flood'] = 'Attack'
    dict_2classes['DoS-TCP_Flood'] = 'Attack'
    dict_2classes['DoS-HTTP_Flood'] = 'Attack'


    dict_2classes['Mirai-greeth_flood'] = 'Attack'
    dict_2classes['Mirai-greip_flood'] = 'Attack'
    dict_2classes['Mirai-udpplain'] = 'Attack'

    dict_2classes['Recon-PingSweep'] = 'Attack'
    dict_2classes['Recon-OSScan'] = 'Attack'
    dict_2classes['Recon-PortScan'] = 'Attack'
    dict_2classes['VulnerabilityScan'] = 'Attack'
    dict_2classes['Recon-HostDiscovery'] = 'Attack'

    dict_2classes['DNS_Spoofing'] = 'Attack'
    dict_2classes['MITM-ArpSpoofing'] = 'Attack'

    dict_2classes['BenignTraffic'] = 'Benign'

    dict_2classes['BrowserHijacking'] = 'Attack'
    dict_2classes['Backdoor_Malware'] = 'Attack'
    dict_2classes['XSS'] = 'Attack'
    dict_2classes['Uploading_Attack'] = 'Attack'
    dict_2classes['SqlInjection'] = 'Attack'
    dict_2classes['CommandInjection'] = 'Attack'

    dict_2classes['DictionaryBruteForce'] = 'Attack'

    model_2_classes = train_and_evaluate_models(training_sets, test_sets, RandomForestClassifier,
                                                 ["RandomForestClassifier (2 classes)"], dict_2classes)

    # Export models
    model_34_classes_file_path = "RandomForest_model_34_classes.joblib"
    model_8_classes_file_path = "RandomForest_model_8_classes.joblib"
    model_2_classes_file_path = "RandomForest_model_2_classes.joblib"
    
    # Export the models
    dump(model_34_classes[0], model_34_classes_file_path)
    dump(model_8_classes[0], model_8_classes_file_path)
    dump(model_2_classes[0], model_2_classes_file_path)

