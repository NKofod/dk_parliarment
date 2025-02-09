"""Provides the functions to fetch data on the current members of
the Danish Parliament using the Open Data of the Parliament.
There may thus be minor inaccuracies in the output, due to
delays in updating on the part of the parliament's Open Data
service.

It provides output as a number of folders, named by the party
short name (eg. "S" for the Social Democrats), containing a number
of .tex files with the output and the images necessary for the
output files. To get pdf output, run XeLaTeX on each of the files.
Also provided in the output is a list of members output in .txt
sorted alphabetically by party and name

A note of caution: As this fetches directly from the Danish Parliament's
Open Data database, the material is in Danish and translation functionality
has not yet been implemented."""
from utils import remove_special_characters


def write_section_to_outfile(inlist, title, data, search_level, searches, output="itemize",
                             section_type="subsection*", only_header=False, constituencies=False):
    # Writes a section to the LaTeX outfile
    # after checking for the existence of the
    # relevant data in the given XML data.
    # Takes as input a filename (file, str),
    # the title of the subsection (title, str),
    # the data being searched (data,var),
    # the number of find operations necessary (search_level,int),
    # the searches to be performed (searches,list) and
    # the format of the output (output, standard is "itemize".
    # Options are "itemize", "paragraph" and "enumerate").
    tmp_var = True
    tmp_list = []
    outlist = list(inlist)
    if only_header:
        outlist.append(str("\{}".format(section_type) + "{" + title + "}\n"))
        return outlist
    # Check for the existence of the relevant data iteratively
    # through the levels of searches specified
    tmp_data = data
    for i in range(search_level):
        # Check for the existence of the given level of search data
        # Simultaneously, if data is present, assign the search
        # result to a variable for later processing
        if tmp_data.find("{}".format(searches[i])) is not None:
            tmp_var = True
            tmp_data = tmp_data.find("{}".format(searches[i]))
        else:
            tmp_var = False
            break
    # If the data is present, continue, else break and end the function
    if tmp_var is True:
        tmp_list.append(str("\{}".format(section_type) + "{" + title + r"}" + "\n"))
        tmp_data = tmp_data.children
        if output == "itemize":
            tmp_list.append(str(r"\begin{itemize}" + "\n"))
            if constituencies:
                tmp_list.append(str(r"\item " + data.find("career").find("currentconstituency").text + "\n"))
            for item in tmp_data:
                item = remove_special_characters(item.text)
                tmp_list.append(str(r"\item " + item + "\n"))
            tmp_list.append(str(r"\end{itemize}" + "\n"))
        elif output == "enumerate":
            tmp_list.append(str(r"\begin{enumerate}" + "\n"))
            for item in tmp_data:
                item = remove_special_characters(item.text)
                tmp_list.append(str(r"\item " + item + "\n"))
            tmp_list.append(str(r"\end{enumerate}" + "\n"))
        elif output == "paragraph":
            for item in tmp_data:
                try: 
                    item = remove_special_characters(item.text)
                except AttributeError:
                    item = remove_special_characters(item)
                except TypeError:
                    item = remove_special_characters(item)
                tmp_list.append(str(item + "\n\n"))
        outlist.extend(tmp_list)
        return outlist
    else:
        if constituencies:
            tmp_list.append(str(r"\subsubsection*{Medlemsperioder}" + "\n"))
            tmp_list.append(str(r"\begin{itemize}" + "\n"))
            tmp_list.append(str(r"\item " + data.find("career").find("currentconstituency").text + "\n"))
            tmp_list.append(str(r"\end{itemize}" + "\n"))
            outlist.extend(tmp_list)
        return outlist


def create_folders_and_files(data):
    import os
    import subprocess
    import re
    import json
    basic_info_dict = {"party-short": "{}".format(data.find("partyshortname").text),
                       "first-name": "{}".format(data.find("firstname").text),
                       "last-name": "{}".format(data.find("lastname").text),
                       "phone": "",
                       "email": "{}".format(remove_special_characters(str(data.find("emails").find("email").text))),
                       "position": "",
                       "party": "{}".format(data.find("party").text)}

    if not os.path.isdir("./party_{}".format(basic_info_dict["party-short"])):
        os.mkdir("./party_{}".format(basic_info_dict["party-short"]))
        os.system("cp -r cv ./party_{}/".format(basic_info_dict["party-short"]))
        os.system("cp -r fonts ./party_{}/".format(basic_info_dict["party-short"]))
        os.system("cp awesome-cv.cls ./party_{}/".format(basic_info_dict["party-short"]))
    # ("Creating {} {}".format(data.find("firstname").text, data.find("lastname").text))
    os.system("cp base_file.tex './party_{}/{}_{}.tex'".format( basic_info_dict["party-short"],
                                                                basic_info_dict["first-name"],
                                                                basic_info_dict["last-name"]))
    picture_url = re.sub("^.+?ft.dk:443", "https://www.ft.dk",
                         str(data.find("picturemires").text))
    picture_name = "{}_{}_profile.jpg".format(basic_info_dict["party-short"],basic_info_dict["first-name"], basic_info_dict["last-name"])
    if not os.path.isfile("./party_{}/{}'".format(  basic_info_dict["party-short"],
                                                    picture_name)):
        os.system("wget -q --no-check-certificate --output-document='./party_{}/{}' {}".format(basic_info_dict["party-short"],
                                                                    picture_name,
                                                                    picture_url))

    for i in ["ministerphone", "phonefolketinget", "mobilephone"]:
        if data.find(i) is not None:
            basic_info_dict["phone"] = str(data.find(i).text)
            # (basic_info_dict["phone"])
            break
    # (basic_info_dict)
    # ("Phone")

    if re.search("minister|folketing|statsrevisor|præsidium", str(data.find("profession").text), re.IGNORECASE):
        basic_info_dict["position"] = str(data.find("profession").text)
    else:
        basic_info_dict["position"] = "Medlem af Folketinget"
    
    
    for i in basic_info_dict.keys():
        os.system("sed -i 's/---{}---/{}/g' './party_{}/{}_{}.tex'".format( i,
                                                                            basic_info_dict[i],
                                                                            basic_info_dict["party-short"],
                                                                            basic_info_dict["first-name"],
                                                                            basic_info_dict["last-name"]))
    outlist = []
    json_file = open("sections.json", "r")
    out_dictionary = json.load(json_file)
    #(out_dictionary)
    for i in out_dictionary.keys():
        
        #(i)
        try: 
            outlist = write_section_to_outfile(outlist,
                                            i,
                                            data,
                                            out_dictionary[i]["search_level"],
                                            out_dictionary[i]["searches"],
                                            output=out_dictionary[i]["output"],
                                            section_type=out_dictionary[i]["section_type"],
                                            only_header=out_dictionary[i]["only_header"],
                                            constituencies=out_dictionary[i]["constituencies"])
        except AttributeError as e:
            print(i)
            print(str(e))
            print(data.find(out_dictionary[i]["searches"][0]))
        except IndexError as e:
            print(i)
            print(str(e))
            print(data.find(out_dictionary[i]["searches"][0]))
    outlist.append(str(r"\end{cvletter}" + "\n"))
    outlist.append(str(r"\end{document}"))
    # ¤# (outlist)
    return outlist


def run_writing_loop(data, memberlist, count):
    import re
    from bs4 import BeautifulSoup as Soup

    for i in range(len(data)):
        if data[i]["biografi"] == None:
            continue
        try:
            xml_data = Soup(data[i]["biografi"], "lxml").find("body").find("member")
            if re.search(r"^.+?\d{1,2}\.\s\w+?\s\d{4}", str(xml_data.find("currentconstituency").text)) is not None:
                memberlist.append("({}) {} {}".format(xml_data.find("partyshortname").text,
                                                      xml_data.find("firstname").text,
                                                      xml_data.find("lastname").text))
                _list = create_folders_and_files(xml_data)
                count += 1
                with open("./party_{}/{}_{}.tex".format(xml_data.find("partyshortname").text,
                                                        xml_data.find("firstname").text,
                                                        xml_data.find("lastname").text), "a") as f:
                    
                    for line in _list:
                        
                        f.write(line)
                print(f"{xml_data.find('firstname').text} {xml_data.find('lastname').text}")
        except AttributeError as e:
            xml_data = Soup(data[i]["biografi"], "lxml")
            
            # #(xml_data)
            first_name = xml_data.find("firstname")
            last_name = xml_data.find("lastname")
            with open("Errors.txt", "a") as f:
                f.write(f"{first_name} {last_name} - {str(e)}\n")
                f.write(str(xml_data))
                f.write("\n\n\n")
        except TypeError as e:
            print(str(data[i]))
            xml_data = Soup(data[i]["biografi"], "lxml")
            # (xml_data)
            first_name = xml_data.find("firstname")
            last_name = xml_data.find("lastname")
            with open("Errors.txt", "a") as f:
                f.write(f"{first_name} {last_name} - {str(e)}\n")
    return memberlist, count


def main():
    import requests
    import json
    url = "https://oda.ft.dk/api/Akt%C3%B8r?$inlinecount=allpages&$filter=typeid%20eq%205"
    data = json.loads(requests.get(url).content)
    list_of_members = []
    counter = 0
    while True:
        try:
            url = data["odata.nextLink"]
            data_json = data["value"]
            list_of_members, counter = run_writing_loop(data_json, list_of_members, counter)
            data = requests.get(url)
            data = json.loads(data.content)
        except KeyError:
            data_json = data["value"]
            list_of_members, counter = run_writing_loop(data_json, list_of_members, counter)
            break
    with open("Current_members.txt", "w") as f:
        for i in list_of_members:
            f.write(f"{i}\n")
    return


if __name__ == '__main__': 
    main()
