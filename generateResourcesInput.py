import os
import configparser
import pandas as pd
import json


# Function to read the properties file
def read_config(config_file='input.properties'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_route_table_dict(keys):
    route_table_dict = {}
    for key in keys:
        route_table_dict[key] = f'rt-{key}'
    return route_table_dict

def get_subnets_dict(keys):
    subnets_dict = {}
    for key in keys:
        subnets_dict[key] = f'sn-{key}'
    return subnets_dict

def get_security_list_dict(keys):
    security_list_dict = {}
    for key in keys:
        security_list_dict[key] = f'sl-{key}'
    return security_list_dict

def get_terraform_resource_name_for_subnets(keys, vcns_list, subnets_dict):
    vcn_prod = None
    vcn_nprod = None
    for vcn in vcns_list:
        for key, value in vcn.items():
            if '-prod' in key:
                vcn_prod = key
            else:
                vcn_nprod = key
    terraform_resource_name_subnet_dict = {}
    for key in keys:
        if '-prod-' in key:
            terraform_resource_name_subnet_dict[key] = f'{vcn_prod}_{subnets_dict[key]}'
        else:
            terraform_resource_name_subnet_dict[key] = f'{vcn_nprod}_{subnets_dict[key]}'
    return terraform_resource_name_subnet_dict

def get_terraform_resource_name_for_security_list(keys, vcns_list, security_list_dict):
    vcn_prod = None
    vcn_nprod = None
    for vcn in vcns_list:
        for key, value in vcn.items():
            if '-prod' in key:
                vcn_prod = key
            else:
                vcn_nprod = key
    terraform_resource_name_sl_dict = {}
    for key in keys:
        if '-prod-' in key:
            terraform_resource_name_sl_dict[key] = f'{vcn_prod}_{security_list_dict[key]}'
        else:
            terraform_resource_name_sl_dict[key] = f'{vcn_nprod}_{security_list_dict[key]}'
    return terraform_resource_name_sl_dict

def get_terraform_resource_name_for_route_table(keys, vcns_list, route_table_dict):
    vcn_prod = None
    vcn_nprod = None
    for vcn in vcns_list:
        for key, value in vcn.items():
            if '-prod' in key:
                vcn_prod = key
            else:
                vcn_nprod = key
    terraform_resource_name_rt_dict = {}
    for key in keys:
        if '-prod-' in key:
            terraform_resource_name_rt_dict[key] = f'{vcn_prod}_{route_table_dict[key]}'
        else:
            terraform_resource_name_rt_dict[key] = f'{vcn_nprod}_{route_table_dict[key]}'
    return terraform_resource_name_rt_dict

def get_vcn(vcn_list):
    vcn_dict = {}
    for vcn in vcn_list:
        vcn_dict['vcn_name'] = f'{vcn}'
        vcn_dict['compartment_id'] = f'{vcn}'
    return vcn_dict

def get_vcn_resources(vcns_list, parent_compartment, vcns_dns_labels_list):
    vcn_resources_list = []
    for vcn in vcns_list:
        for key, value in vcn.items():
            vcn_res_item = {}
            vcn_res_item['vcn_name'] = f'{key}'
            vcn_res_item['compartment_id'] = f'{parent_compartment}'
            vcn_res_item['cidr_block'] = f'{value}'
            vcn_res_item['display_name'] = f'{key}'
            for vcn_dns_label in vcns_dns_labels_list:
                for k, v in vcn_dns_label.items():
                    if key == k:
                        vcn_res_item['dns_label'] = f'{v}'
                        break
            vcn_resources_list.append(vcn_res_item)

    return vcn_resources_list

def get_route_tables_resources(route_table_dict, compartments_list, vcns_list, terraform_resource_name_rt_dict):
    route_table_resources_list = []
    for key, value in route_table_dict.items():
        route_table_item = {}
        route_table_item['route_table_name'] = f"{terraform_resource_name_rt_dict[key]}"
        if route_table_item['route_table_name'] == 'vcn-spoke-adc-sysdig-priv-nprod_rt-spoke-adc-sysdig-priv-dev-oke-worker':
            print(f'route_table_item: {route_table_item}')

        if '-prod' in route_table_item['route_table_name']:
            for compartment in compartments_list:
                if '-prod' in compartment:
                    route_table_item['compartment_id'] = f'{compartment}'
                    break
        else:
            for compartment in compartments_list:
                if '-prod' not in compartment:
                    route_table_item['compartment_id'] = f'{compartment}'

        if '-prod' in route_table_item['route_table_name']:
            for vcn in vcns_list:
                if '-prod' in vcn:
                    route_table_item['vcn_id'] = f'{vcn}'
                    break
        else:
            for vcn in vcns_list:
                if '-prod' not in vcn:
                    route_table_item['vcn_id'] = f'{vcn}'

        route_table_item['display_name'] = f'{value}'
        route_table_item['route_rules_drg'] = ''
        route_table_item['freeform_tags'] = ''
        route_table_item['route_rules_igw'] = ''
        route_table_item['route_rules_sgw'] = ''
        route_table_item['route_rules_ngw'] = ''
        route_table_item['route_rules_lpg'] = ''
        route_table_item['route_rules_ip'] = ''
        route_table_item['defined_tags'] = ''
        
        route_table_resources_list.append(route_table_item)

    return route_table_resources_list



def main():
    # get current script directory path
    script_dir = os.path.dirname(os.path.realpath(__file__))
    print(f'script_dir: {script_dir}')

    # form file path for input.properties using script_dir
    input_config_file = os.path.join(script_dir, 'input.properties')

    # read from input.properties
    input_config = read_config(input_config_file)
    resource_name = input_config.get('RESOURCES', 'resource_name')
    print(f'resource_name: {resource_name}')

    # read parent compartment from input.properties
    parent_compartment = input_config.get('COMPARTMENTS', 'parent_compartment')
    print(f'parent_compartment: {parent_compartment}')

    # read compartments from input.properties
    # compartments=cmp-adc-sysdig,cmp-adc-sysdig-dev,cmp-adc-sysdig-prod
    compartments = input_config.get('COMPARTMENTS', 'compartments')
    compartments_list = compartments.split(',')
    print(f'compartments_list: {compartments_list}')

    # read groups from input.properties
    groups = input_config.get('GROUPS', 'groups')
    groups_list = groups.split(',')
    print(f'groups_list: {groups_list}')

    # read groups from input.properties
    vcns = input_config.get('VCNS', 'vcns')
    vcns_list = vcns.split(',')
    print(f'vcns_list: {vcns_list}')

    # read vcns from input.properties
    vcns_cidrs = input_config.get('VCNS', 'vcns_cidrs')
    vcns_cidrs = vcns_cidrs.replace("'", '"')
    try:
        vcns_cidrs_list = json.loads(vcns_cidrs)
        for vcn_cidr in vcns_cidrs_list:
            for key, value in vcn_cidr.items():
                print(f'{key}: {value}')
    except json.JSONDecodeError as e:
        print(f"Error parsing vcns_cidrs: {e}")

    # read vcns_dns_labels from input.properties
    vcns_dns_labels = input_config.get('VCNS', 'vcns_dns_labels')
    vcns_dns_labels = vcns_dns_labels.replace("'", '"')
    try:
        vcns_dns_labels_list = json.loads(vcns_dns_labels)
        # print(f'vcns_dns_labels_list: {vcns_dns_labels_list}')
        for vcn_dns_label in vcns_dns_labels_list:
            for key, value in vcn_dns_label.items():
                print(f'{key}: {value}')
            # print(f'vcn_dns_label: {vcn_dns_label}')
    except json.JSONDecodeError as e:
        print(f"Error parsing vcns_dns_labels: {e}")

     # read subnets from input.properties
    subnets = input_config.get('SUBNETS', 'subnets')
    subnets_list = subnets.split(',')
    print(f'subnets_list: {subnets_list}')

    keys = []
    for subnet in subnets_list:
        keys.append(subnet[3:])
        print(f'subnet: {subnet}')

    # read subnet_cidrs from input.properties
    subnet_cidrs = input_config.get('SUBNETS', 'subnet_cidrs')
    subnet_cidrs = subnet_cidrs.replace("'", '"')
    cidr_dict = dict()
    try:
        subnet_cidrs_list = json.loads(subnet_cidrs)
        # print(f'subnet_cidrs_list: {subnet_cidrs_list}')
        for subnet_cidr in subnet_cidrs_list:
            for key, value in subnet_cidr.items():
                cidr_dict[key[3:]] = value
                print(f'{key}: {value}')
            # print(f'subnet_cidr: {subnet_cidr}')
    except json.JSONDecodeError as e:
        print(f"Error parsing subnet_cidrs: {e}")

    # print('***'*80)
    # print(f'cidr_dict: ')
    # for key, value in cidr_dict.items():
    #     print(f'{key}: {value}')
    # print('-'*20)

    # # print(f'keys: {keys}')
    # for key in keys:
    #     print(f'key: {key}')

    # get route table dictionary
    route_table_dict = get_route_table_dict(keys)
    print('-'*20)
    # print(f'route_table_dict: {route_table_dict}')
    # pretty print route_table_dict
    for key, value in route_table_dict.items():
        print(f'{key}: {value}')
    print('-'*20)

    # get subnets dictionary
    subnets_dict = get_subnets_dict(keys)
    print('-'*20)
    # print(f'subnets_dict: {subnets_dict}')
    # pretty print subnets_dict
    for key, value in subnets_dict.items():
        print(f'{key}: {value}')
    print('-'*20)

    # get security list dictionary
    security_list_dict = get_security_list_dict(keys)
    print('-'*20)
    # print(f'security_list_dict: {security_list_dict}')
    # pretty print security_list_dict
    for key, value in security_list_dict.items():
        print(f'{key}: {value}')
    print('-'*20)

    terraform_resource_name_subnet_dict = get_terraform_resource_name_for_subnets(keys, vcns_cidrs_list, subnets_dict)
    print('-'*20)
    # print(f'terraform_resource_name_subnet_dict: {terraform_resource_name_subnet_dict}')
    # pretty print terraform_resource_name_subnet_dict
    for key, value in terraform_resource_name_subnet_dict.items():
        print(f'{key}: {value}')
    print('-'*20)

    terraform_resource_name_sl_dict = get_terraform_resource_name_for_security_list(keys, vcns_cidrs_list, security_list_dict)
    print('-'*20)
    # print(f'terraform_resource_name_sl_dict: {terraform_resource_name_sl_dict}')
    # pretty print terraform_resource_name_sl_dict
    for key, value in terraform_resource_name_sl_dict.items():
        print(f'{key}: {value}')
    print('-'*20)
    
    terraform_resource_name_rt_dict = get_terraform_resource_name_for_route_table(keys, vcns_cidrs_list, route_table_dict)
    print('-'*20)
    # print(f'terraform_resource_name_rt_dict: {terraform_resource_name_rt_dict}')
    # pretty print terraform_resource_name_rt_dict
    print(f'terraform_resource_name_rt_dict: ')
    for key, value in terraform_resource_name_rt_dict.items():
        print(f'{key}: {value}')
    print('-'*20)


    print('='*80)





    resource_vcns = get_vcn_resources(vcns_cidrs_list, parent_compartment, vcns_dns_labels_list)
    print('-'*20)
    # print(f'resource_vcn: {resource_vcn}')
    # pretty print resource_vcn
    for vcn in resource_vcns:
        print(f'vcn_name: {vcn["vcn_name"]}')
        print(f'compartment_id: {vcn["compartment_id"]}')
        print(f'cidr_block: {vcn["cidr_block"]}')
        print(f'display_name: {vcn["display_name"]}')
        print(f'dns_label: {vcn["dns_label"]}')
        print('-'*20)

    resource_route_tables = get_route_tables_resources(route_table_dict, compartments_list, vcns_list, terraform_resource_name_rt_dict)
    print('-'*20)
    # print(f'resource_route_tables: {resource_route_tables}')
    # pretty print resource_route_tables
    for route_table in resource_route_tables:
        print(f'route_table_name: {route_table["route_table_name"]}')
        print(f'compartment_id: {route_table["compartment_id"]}')
        print(f'vcn_id: {route_table["vcn_id"]}')
        print(f'display_name: {route_table["display_name"]}')
        print(f'route_rules_drg: {route_table["route_rules_drg"]}')
        print(f'freeform_tags: {route_table["freeform_tags"]}')
        print(f'route_rules_igw: {route_table["route_rules_igw"]}')
        print(f'route_rules_sgw: {route_table["route_rules_sgw"]}')
        print(f'route_rules_ngw: {route_table["route_rules_ngw"]}')
        print(f'route_rules_lpg: {route_table["route_rules_lpg"]}')
        print(f'route_rules_ip: {route_table["route_rules_ip"]}')
        print(f'defined_tags: {route_table["defined_tags"]}')
        print('-'*20)





    # Get unique environments
    environments = list({env.split('-')[0] for env in subnets_dict.keys()})
    print(f'environments: {environments}')

    # Create an empty DataFrame to hold the final data
    terraform_final_df = pd.DataFrame()

    # Loop through each environment
    for environment in environments:
        print(f'Processing environment: {environment}')
        # Filter out the subnets, security lists, and route tables for the current environment
        sn_for_env = {k: v for k, v in subnets_dict.items() if k.startswith(environment)}
        cidr_for_env = {k: v for k, v in cidr_dict.items() if k.startswith(environment)}
        sl_for_env = {k: v for k, v in security_list_dict.items() if k.startswith(environment)}
        rt_for_env = {k: v for k, v in route_table_dict.items() if k.startswith(environment)}
        tf_res_name_for_sn = {k: v for k, v in terraform_resource_name_subnet_dict.items() if k.startswith(environment)}
        tf_res_name_for_sl = {k: v for k, v in terraform_resource_name_sl_dict.items() if k.startswith(environment)}
        tf_res_name_for_rt = {k: v for k, v in terraform_resource_name_rt_dict.items() if k.startswith(environment)}

        # Loop through each subnet
        for key in keys:
            print(f'Processing key: {key}')

            # Create a DataFrame for this combination
            data = {
                'key': [key],
                'subnet': [sn_for_env[key]],
                'cidr': [cidr_for_env[key]],
                'security_list': [sl_for_env[key]],
                'route_table': [rt_for_env[key]],
                'terraform_resource_name_for_subnet': [tf_res_name_for_sn[key]],
                'terraform_resource_name_for_security_list': [tf_res_name_for_sl[key]],
                'terraform_resource_name_for_route_table': [tf_res_name_for_rt[key]]
            }
            df = pd.DataFrame(data)

            # Use pd.concat instead of df.append
            terraform_final_df = pd.concat([terraform_final_df, df], ignore_index=True)

    # Print the final DataFrame
    print(terraform_final_df)

    # form file path for excel file using script_dir
    excel_file = os.path.join(script_dir, 'resources2.xlsx')
    print(f'excel_file: {excel_file}')

    # write to excel file
    # rename sheet name to 'input
    terraform_final_df.to_excel(excel_file, index=False)
    print(f'excel file created successfully: {excel_file}')




if __name__ == "__main__":
    main()

