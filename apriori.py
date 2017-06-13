import sys
import csv


class APRIORI(object):
    def __init__(apriori, datafile, min_sup, min_conf, data):
        apriori.datafile = datafile
        apriori.min_sup = float(min_sup)
        apriori.min_conf = float(min_conf)
        apriori.data = data
        apriori.records=[]
        apriori.itemsets = []
        apriori.rules ={}

# converts dat file into csv file
    def convert_into_csv(apriori):
        with open(apriori.datafile, 'r') as input_file:
            lines = input_file.readlines()
            transactions = []
            for line in lines:
                transaction = line.strip().split(" ")
                transactions.append(transaction)
		
        with open(apriori.data, 'w',newline='') as output_file:
            for trans in transactions:
                if len(trans)>0:
                    file_writer = csv.writer(output_file)
                    file_writer.writerow(trans)
        return output_file

#Loads the csv file generated and scans dataset to create first itemsets with count of each element
    def load_data(apriori):
        C_1 = dict()
        item_writer = open('itemsets.txt', 'w')
        for readline in open(apriori.data, 'r'):
            for line in readline.split('\r'):
                #print(line)
# filters the empty columns in the rows,so they won't appear in itemsets
                row = line.strip().split(',')
                row = list(filter(None,row))
                apriori.records.append(set(row))
                for item in row:
                    item_set = frozenset([item])
                    if item_set not in C_1:
                        C_1[item_set]=1
                    else:
                        C_1[item_set]+=1
        item_writer.write('1-itemsets C1:'+str(C_1)+'\n')
        apriori.itemsets.append(C_1)
        apriori.gen_freq_1_itemset()

#function which scan the data and removes the itemsets whose support value is below minimum support value.
    def gen_freq_1_itemset(apriori):
        num_records  = len(apriori.records)
        L_1 = apriori.itemsets[0]
        for item in list(L_1):
            sup_value = float(L_1[item])/num_records
            if apriori.min_sup > sup_value:
                del L_1[item]
            else:
                L_1[item] = sup_value
        apriori.itemsets[0] = L_1

# Generates k+1 itemsets based on k-itemsets generated previously and also calculates their support values
    def gen_freq_k_itemsets(apriori):
        base_set = list(apriori.itemsets[0])
        while len(base_set) is not 0:
            itemset_len = len(base_set[0])+1
            candidate_itemsets = dict()
            for i in range(0, len(base_set)):
                for j in range(i+1, len(base_set)):
                    currentset = base_set[i] | base_set[j]
                    if len(currentset) is itemset_len:
                        count = 0
                        for set in base_set:
                            if set <= currentset:
                                count += 1
                        if count == len(currentset):
                            candidate_itemsets[currentset] = 0
            if len(candidate_itemsets) is not 0:
                for record in apriori.records:
                    for cand_set in candidate_itemsets:
                        if cand_set <= record:
                            candidate_itemsets[cand_set] += 1
                for cand_set in list(candidate_itemsets):
                    support_value = float(candidate_itemsets[cand_set])/len(apriori.records)
                    if support_value < apriori.min_sup:
                        del candidate_itemsets[cand_set]
                    else:
                        candidate_itemsets[cand_set] = support_value
            if len(candidate_itemsets) is not 0:
                apriori.itemsets.append(candidate_itemsets)
            base_set = list(candidate_itemsets)

    def truncate(apriori,val, n):
        s = '{}'.format(val)
        if 'e' in s or 'E' in s:
            return '{0:.{1}f}'.format(val, n)
        i, p, d = s.partition('.')
        return '.'.join([i, (d+'0'*n)[:n]])
		
# generates rules among itemsets using the minimum confidence value
    def generate_rules(apriori):
        apriori.gen_freq_k_itemsets()
        for itemsets in apriori.itemsets[1:]:
            for set in list(itemsets):
                for item in set:
                    left_items = set - frozenset([item])
                    item_conf = float(apriori.itemsets[len(set) - 1][set]) / (apriori.itemsets[len(left_items) - 1][left_items])
                    if apriori.min_conf <= item_conf:
                        rule = "[" + ", ".join(list(left_items)) + "] => [" + item + "] (Confidence: "+apriori.truncate(str(item_conf * 100),5) + "%, Support: " + apriori.truncate(str((itemsets[set] * 100)),5) + "%)"
                        apriori.rules[rule] = item_conf


# Print frequent itemsets and association rules with their support value and confidence
    def apriori_output_to_file(apriori):
        writer = open('output.txt', 'w')
        writer.write('Dataset used : '+ apriori.datafile+'\n')
        writer.write('Dataset converted to : '+ apriori.data+'\n')
        writer.write('Minimum Support: '+str(apriori.min_sup*100)+'%\n')
        writer.write('Minimum Confidence: '+str(apriori.min_conf*100)+'%\n')
        all_itemsets = []
        for itemsets in apriori.itemsets:
            all_itemsets+=itemsets
        writer.write('\nFrequent itemsets and their support values\n')
        for itemset in all_itemsets:
            writer.write(str(list(itemset)))
            writer.write(', Support:' + apriori.truncate(str(apriori.itemsets[len(itemset)-1][itemset]*100),5) + '%')
            writer.write('\n')
        writer.write('\nAssociation rules and their support and confidence values \n')
        for rules in apriori.rules.keys():
            writer.write(rules)
            writer.write('\n')
        writer.write('\nMinimum support and minimum confidence are user defined values given as arguments with the command. All the values of support and confidence are truncated to 5 decimals while displaying output.')
        writer.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Inputs required are: [DATASET] [min_sup] [min_conf]")
        sys.exit(2)
    apr = APRIORI(sys.argv[1],sys.argv[2], sys.argv[3],'data.csv')
    apr.convert_into_csv()
    apr.load_data()
    apr.generate_rules()
    apr.apriori_output_to_file()

print("Done")