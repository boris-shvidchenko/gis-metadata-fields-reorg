import xml.etree.ElementTree as xml  
import arcpy

# === OBTAINS THE WORKSPACE LOCATION (GDB) ===

gdb = arcpy.GetParameterAsText(0)                                                           # Obtains/sets up the workspace 
arcpy.env.workspace = gdb                                                                   # Message is added to confirm that the workspace has been chosen
arcpy.AddMessage("{0} is the gdb being used.".format(gdb))                  

# === OBTAINS THE FEATURE ===

feature = arcpy.GetParameterAsText(1)                                                       # Obtains the feature
if ".SDE." in feature:                                                                      # Message is added to confirm that the feature has been chosen
    feature_split = feature.split(".SDE.")
    feature_short_name = feature_split[1]
    arcpy.AddMessage("{0} is the feature class.".format(feature_short_name))    
else:
    arcpy.AddMessage("{0} is the feature class.".format(feature))

# === OBTAINS THE FEATURE METADATA AS XML ===
 
feature_metadata = arcpy.metadata.Metadata(feature)                                         # Identifies and exports the metadata, of the feature, in xml format
feature_md_name = "{0}.xml".format(feature)                                                 # Message is added to confirm that the metadata xml file has been exported
feature_metadata.exportMetadata(feature_md_name,"FGDC_CSDGM")

temp = feature_md_name.split("\\")                                                          
feature_md_short_name = temp[-1]
if ".SDE." in feature:
    feature_metadata.exportMetadata("{0}.xml".format(feature_short_name),"FGDC_CSDGM")
    arcpy.AddMessage("Metadata for {0} has been exported.".format(feature_short_name))
else:
    feature_metadata.exportMetadata("{0}.xml".format(feature),"FGDC_CSDGM")
    arcpy.AddMessage("Metadata for {0} has been exported.".format(feature))     

# === CREATES ORDERED LIST OF FIELDS FROM THE FEATURE ===

field_list = [field.name for field in arcpy.ListFields(feature)]                            # Creates an ordered list of fields 
                                                                                            # The order of the fields is based on the order of which they appear in the feature attribute table
# === OPENS AND EXTRACTS DATA FROM XML FILE ===

tree = xml.parse(feature_md_name)
root = tree.getroot()                                                                       # Obtains the root of all data in the exported metadata xml file

metadata_field_list = []
for section in root.findall("eainfo"):                                                      # Parses through the metadata xml file and saves all elements into 'metadata_field_list'
    detailed = section.find("detailed")                                                     # Each element is saved with the corresponding field name, this is so that metadata elements can have a reference
    for attr in detailed.findall("attr"):                           
        attr_list = []                                              
        field_name = attr.find("attrlabl").text                     
        attr_list.append(field_name)                                
        attr_list.append(attr)
        metadata_field_list.append(attr_list)                       

# === ORGANIZES ATTRIBUTE DATA INTO CORRECT ORDER ===

final_metadata_field_list = []
for name in field_list:                                                                     # Reorganizes 'metadata_field_list' so that the fields and elements from the metadata xml file match...
    for field in metadata_field_list:                                                       # ...the order of the fields from the feature attribute table
        if field[0] == name:                                                                # Field names are crossreferenced to maintain the correct order
            sub_list = []
            sub_list.append(field[0]) 
            sub_list.append(field[1]) 
            final_metadata_field_list.append(sub_list)
        elif field[0] != name:                                                              # In some cases the field names, between the xml file and the attribute table, are different
            if ".STLength()" in field[0] and "Shape_Length" in name:                        # These field name differences can be hardcoded here, under the first 'elif' statement
                sub_list = []
                sub_list.append(field[0]) 
                sub_list.append(field[1]) 
                final_metadata_field_list.append(sub_list)
            elif ".STArea()" in field[0] and "Shape_Area" in name:
                sub_list = []
                sub_list.append(field[0]) 
                sub_list.append(field[1]) 
                final_metadata_field_list.append(sub_list)
            else:
                continue
        else:
            continue

# === UPDATES, "ATTRLABL", LABEL IN XML FILE === 

label_list = []
counter = 0
for i in final_metadata_field_list:                                                         # Obtains the 'attrlabl' subelement, for each parent element, and stores it as text in label_list 
    attrlabl = i[1].find("attrlabl")                                                    
    if attrlabl != None: 
        label_sub_list = []
        temp_elem = final_metadata_field_list[counter]
        temp_elem = temp_elem[0]
        label_sub_list.append(temp_elem)
        attrlabl = i[1].find("attrlabl").text
        label_sub_list.append(attrlabl)
        label_list.append(label_sub_list)
        counter += 1
    else:
        counter += 1
counter = 0
for attr in detailed.iter("attrlabl"):                                                      # Updates the 'attrlabl' subelement in the xml file, based on the stored text in label_list
    while True:                                                                             # Field names are crossreferenced to maintain the correct order
        labl = label_list[counter]
        labl = labl[1]
        if labl in field_list:
            attr.clear()
            attr.text = labl
            counter += 1
            break
        elif labl not in field_list:                                                        # In some cases the field names, between the xml file and the attribute table, are different
            if ".STLength()" in labl and "Shape_Length" in field_list:                      # These field name differences can be hardcoded here, under the first 'elif' statement
                attr.clear()
                attr.text = labl
                counter += 1
                break 
            elif ".STArea()" in labl and "Shape_Area" in field_list:
                attr.clear()
                attr.text = labl
                counter += 1
                break
            else:
                continue
        else:
            counter += 1
            break
    if counter < len(label_list):                                                           # A counter variable is used to ensure that an 'IndexError' is avoided 
        continue
    else:
        break

# === UPDATES, "ATTRDEF", DEFINITION IN XML FILE ===

def_list = []
counter = 0
for i in final_metadata_field_list:                                                         # Obtains the 'attrdef' subelement, for each parent element, and stores it as text in def_list
    attrdef = i[1].find("attrdef")
    if attrdef != None:
        def_sub_list = []
        temp_elem = final_metadata_field_list[counter]
        temp_elem = temp_elem[0]
        def_sub_list.append(temp_elem)
        attrdef = i[1].find("attrdef").text
        def_sub_list.append(attrdef)
        def_list.append(def_sub_list)
        counter += 1
    else:
        counter += 1
counter = 0
for attr in detailed.iter("attrdef"):                                                       # Updates the 'attrdef' subelement in the xml file, based on the stored text in def_list
    while True:                                                                             # Field names are crossreferenced to maintain the correct order
        defi = def_list[counter]
        defi_label = defi[0]
        defi = defi[1]
        if defi_label in field_list:   
            attr.clear()
            attr.text = defi
            counter += 1
            break
        elif defi_label not in field_list:                                                  # In some cases the field names, between the xml file and the attribute table, are different
            if ".STLength()" in defi_label and "Shape_Length" in field_list:                # These field name differences can be hardcoded here, under the first 'elif' statement
                attr.clear()
                attr.text = defi
                counter += 1
                break 
            elif ".STArea()" in defi_label and "Shape_Area" in field_list:
                attr.clear()
                attr.text = defi
                counter += 1
                break
            else:
                continue
        else:
            counter += 1
            break
    if counter < len(def_list):                                                             # A counter variable is used to ensure that an 'IndexError' is avoided 
        continue
    else:
        break

# === UPDATES, "ATTRDEFS", DESCRIPTION SOURCE IN XML FILE ===

source_list = []
counter = 0
for i in final_metadata_field_list:                                                         # Obtains the 'attrdefs' subelement, for each parent element, and stores it as text in def_list
    attrdefs = i[1].find("attrdefs")
    if attrdefs != None:
        defs_sub_list = []
        temp_elem = final_metadata_field_list[counter]
        temp_elem = temp_elem[0]
        defs_sub_list.append(temp_elem)
        attrdefs = i[1].find("attrdefs").text
        defs_sub_list.append(attrdefs)
        source_list.append(defs_sub_list)
        counter += 1
    else:
        counter += 1
counter = 0
for attr in detailed.iter("attrdefs"):                                                      # Updates the 'attrdefs' subelement in the xml file, based on the stored text in defs_list
    while True:                                                                             # Field names are crossreferenced to maintain the correct order
        source = source_list[counter]
        source_label = source[0]
        source_elem = source[1]
        if source_label in field_list:
            attr.clear()
            attr.text = source_elem
            counter += 1
            break
        elif source_label not in field_list:                                                # In some cases the field names, between the xml file and the attribute table, are different
            if ".STLength()" in source_label and "Shape_Length" in field_list:              # These field name differences can be hardcoded here, under the first 'elif' statement
                attr.clear()
                attr.text = source_elem
                counter += 1
                break 
            elif ".STArea()" in source_label and "Shape_Area" in field_list:
                attr.clear()
                attr.text = source_elem
                counter += 1
                break
            else:
                continue
        else:
            counter += 1
            break
    if counter < len(source_list):                                                          # A counter variable is used to ensure that an 'IndexError' is avoided 
        continue
    else:
        break

# === FINDS AND STORES ALL UDOM ELEMENTS IN LIST ===

domv_list = []  
udom_list = []  
counter = 0     

for i in final_metadata_field_list:                                                         # Iterates through 'final_metadata_field_list' and obtains all 'domv' subelements
    domv_sublist = []                                                                       # A counter variable is used to ensure that an 'IndexError' is avoided 
    attrdomv = i[1].find("attrdomv")       
    if attrdomv != None:                    
        domv_sublist.append(field_list[counter])    
        domv_sublist.append(attrdomv)               
        domv_list.append(domv_sublist)              
        counter += 1
    else:
        counter += 1
        continue

for i in domv_list:                                                                         # Iterates through 'domv_list' and obtains all 'udom' subelements               
    attrudom = i[1].find("udom")                                                            # A counter variable is used to ensure that an 'IndexError' is avoided 
    if attrudom != None:                
        udom_sublist = []               
        udom_sublist.append(i[0])       
        udom_sublist.append(attrudom.text)  
        udom_list.append(udom_sublist)      
    else:
        continue

# === FINDS AND STORES ALL EDOM ELEMENTS IN LIST ===

edom_list = []                              
for domv in domv_list:                                                                      # Iterates through 'domv_list' and obtains all 'edom' subelements
    domv_edom = domv[1].findall("edom")     
    if len(domv_edom) != 0:                 
        edom_sublist = []                   
        domv_labl = domv[0]                 
        edom_sublist.append(domv_labl)      
        edom_sublist.append(domv_edom)      
        edom_list.append(edom_sublist)      
    else:
        continue

# === FINDS AND STORES ALL EDOMV ELEMENTS IN LIST ===

edomv_list = []                                 
for edomv in edom_list:                                                                     # Iterates through 'domv_list' and obtains all 'edomv' subelements
    edomv_elem = edomv[1]                       
    try:
        for elem in edomv_elem:                     
            domv_edomv = elem.find("edomv").text    
            edomv_list.append(domv_edomv)           
    except AttributeError:
        continue
    
# === FINDS AND STORES ALL EDOMVD ELEMENTS IN LIST ===

edomvd_list = []                                
for edomvd in edom_list:                                                                    # Iterates through 'domv_list' and obtains all 'edomvd' subelements
    edomvd_elem = edomvd[1]                     
    try:
        for elem in edomvd_elem:                    
            domv_edomvd = elem.find("edomvd").text  
            edomvd_list.append(domv_edomvd)         
    except AttributeError:
        continue
    
# === FINDS AND STORES ALL EDOMVDS ELEMENTS IN LIST ===

edomvds_list = []                                
for edomvds in edom_list:                                                                   # Iterates through 'domv_list' and obtains all 'edomvds' subelements                     
    edomvds_elem = edomvds[1]                    
    try:
        for elem in edomvds_elem:                    
            domv_edomvds = elem.find("edomvds").text 
            edomvds_list.append(domv_edomvds)        
    except AttributeError:
        continue
    
# === FINDS AND STORES ALL RDOM ELEMENTS IN LIST ===

rdom_list = []                              
for domv in domv_list:                                                                      # Iterates through 'domv_list' and obtains all 'rdom' subelements
    domv_rdom = domv[1].findall("rdom")     
    if len(domv_rdom) != 0:                 
        rdom_sublist = []                   
        domv_labl = domv[0]                 
        rdom_sublist.append(domv_labl)      
        rdom_sublist.append(domv_rdom)      
        rdom_list.append(rdom_sublist)      
    else:
        continue

# === FINDS AND STORES ALL RDOMMIN ELEMENTS IN LIST ===

rdommin_list = []                                                          
for rdommin in rdom_list:                                                                   # Iterates through 'domv_list' and obtains all 'rdommin' subelements
    rdommin_elem = rdommin[1]                    
    try:
        for elem in rdommin_elem:                    
            domv_rdommin = elem.find("rdommin").text 
            rdommin_list.append(domv_rdommin)        
    except AttributeError:
        continue
    
# === FINDS AND STORES ALL RDOMMAX ELEMENTS IN LIST ===

rdommax_list = []                                   
for rdommax in rdom_list:                                                                   # Iterates through 'domv_list' and obtains all 'rdommax' subelements
    rdommax_elem = rdommax[1]                    
    try:
        for elem in rdommax_elem:                    
            domv_rdommax = elem.find("rdommax").text 
            rdommax_list.append(domv_rdommax)             
    except AttributeError:
        continue
    
# === FINDS AND STORES ALL ATTRUNIT ELEMENTS IN LIST ===

attrunit_list = []                                  
for attrunit in rdom_list:                                                                  # Iterates through 'domv_list' and obtains all 'attrunit' subelements
    attrunit_elem = attrunit[1]                     
    try:
        for elem in attrunit_elem:                      
            domv_attrunit = elem.find("attrunit").text  
            attrunit_list.append(domv_attrunit)         
    except AttributeError:
        continue
           
# === FINDS AND STORES ALL ATTRMRES ELEMENTS IN LIST ===

attrmres_list = []                                   
for attrmres in rdom_list:                                                                  # Iterates through 'domv_list' and obtains all 'attrmres' subelements
    attrmres_elem = attrmres[1]                     
    try:
        for elem in attrmres_elem:                      
            domv_attrmres = elem.find("attrmres").text  
            attrmres_list.append(domv_attrmres)               
    except AttributeError:
        continue
    
# === CHECKS IF "ATTRDOMV" EXISTS IN ELEMENT, UPDATES XML IF IT DOES ===

metadata_attrdomv_list = []                     
for name in field_list:                                                                     # Crossreferences metadata field names with attribute field names, matching fields get stored in 'metadata_attrdomv_list'
    for field in final_metadata_field_list:
        if field[0] == name:
            metadata_attrdomv_list.append(field)
        elif field[0] != name:
            if ".STLength()" in field[0] and "Shape_Length" in name:
                metadata_attrdomv_list.append(field)
            elif ".STArea()" in field[0] and "Shape_Area" in name:
                metadata_attrdomv_list.append(field)
        else:
            continue
counter = 0
for attr in root.iter("attr"):                                                              # Updates all 'attrdomv' subelements 
    try:                                                                                    # A counter variable is used to ensure that an 'IndexError' is avoided, in this case a try/except statement is also included 
        for attrdomv in attr.findall("attrdomv"):
            attr.remove(attrdomv)
        elem_label = field_list[counter]         
        for field in final_metadata_field_list:                                             # Creates a new 'attrdomv' subelement  
            if field[0] == elem_label:                                                      # In some cases the field names are different, and there is an error in matching
                try:                                                                        # Known field names that are different can be hardcoded here, below the second try statement
                    attrdomv_elem = field[1].find("attrdomv")    
                    if attrdomv_elem != None:                                                               
                        new_domv_elem = xml.Element("attrdomv")      
                        attr.insert(3, new_domv_elem)
                    elif attrdomv_elem == None and field[0] == "OBJECTID" or field[0] == "OBJECTID_1":
                        new_domv_elem = xml.Element("attrdomv")      
                        attr.insert(3, new_domv_elem)
                    elif attrdomv_elem == None and field[0] == "DETAW" or field[0] == "ACRES":
                        new_domv_elem = xml.Element("attrdomv")      
                        attr.insert(3, new_domv_elem)
                    else:   
                        continue               
                except:
                    continue
            elif field[0] != elem_label:                                                    # Replicates the function of the first if statement above, but checks additional criteria if no matches are found
                if ".STLength()" in field[0] and "Shape_Length" in elem_label:
                    try:
                        attrdomv_elem = field[1].find("attrdomv")   
                        if attrdomv_elem != None:                   
                            new_domv_elem = xml.Element("attrdomv")      
                            attr.insert(3, new_domv_elem)
                        else:   
                            continue               
                    except:
                        continue
                elif ".STArea()" in field[0] and "Shape_Area" in elem_label:
                    try:
                        attrdomv_elem = field[1].find("attrdomv")   
                        if attrdomv_elem != None:                   
                            new_domv_elem = xml.Element("attrdomv")      
                            attr.insert(3, new_domv_elem)
                        else:   
                            continue               
                    except:
                        continue
            else:
                continue
        if counter <= len(field_list):                                                      # A counter variable is used to ensure that an 'IndexError' is avoided 
            counter += 1
        else:
            break
    except IndexError:                                                                      # A second 'IndexError' check, skips if such an error occurs 
        continue

# === CREATES AND UPDATES "UDOM" IN "ATTRDOMV" IN XML FILE ===

counter = 0
for attr in detailed.iter("attr"):                                                          # Updates all 'udom' subelements       
    labl = attr.find("attrlabl").text                                                       # A counter variable is used to ensure that an 'IndexError' is avoided
    for name in udom_list:                  
        if name[0] == labl:                 
            try:
                attr_udom = attr.find("attrdomv")   
                if attr_udom != None:                                                       # Creates a new 'udom' subelement
                    new_udom_elem = xml.Element("udom")                                     # In some cases the field names are different, and there is an error in matching
                    attr_udom.insert(0, new_udom_elem)                                      # Known field names that are different can be hardcoded here, below the first elif statement
                    udom_elem = udom_list[counter]
                    udom_elem = udom_elem[1]
                    new_udom_elem.text = udom_elem      
                    counter += 1 
                else:
                    continue
            except:
                continue
        elif name[0] != labl:                                                               # Known field names that are different can be hardcoded here
            if "Shape_Length" in name[0] and ".STLength()" in labl:
                try:
                    attr_udom = attr.find("attrdomv")   
                    if attr_udom != None:               
                        new_udom_elem = xml.Element("udom") 
                        attr_udom.insert(0, new_udom_elem)  
                        udom_elem = udom_list[counter]
                        udom_elem = udom_elem[1]
                        new_udom_elem.text = udom_elem      
                        counter += 1 
                    else:
                        continue
                except:
                    continue
            elif "Shape_Area" in name[0] and ".STArea()" in labl:
                try:
                    attr_udom = attr.find("attrdomv")   
                    if attr_udom != None:               
                        new_udom_elem = xml.Element("udom") 
                        attr_udom.insert(0, new_udom_elem)  
                        udom_elem = udom_list[counter]
                        udom_elem = udom_elem[1]
                        new_udom_elem.text = udom_elem      
                        counter += 1 
                    else:
                        continue
                except:
                    continue
        else:
            continue       
    
# === CREATES AND UPDATES "EDOM" IN "ATTRDOMV" IN XML FILE ===

counter = 0
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'edom' subelement  
    labl = attr.find("attrlabl").text                                                       # Field names are crossreferenced to ensure correct order
    for name in edom_list:                  
        if name[0] == labl:                 
            try:
                attr_edom = attr.find("attrdomv")   
                if attr_edom != None:               
                    num = True              
                    counter2 = 0            
                    while num:
                        new_edom_elem = xml.Element("edom") 
                        attr_edom.insert(0, new_edom_elem)  
                        counter2 += 1
                        if counter2 < len(name[1]):                                         # A counter variable is used to ensure that an 'IndexError' is avoided
                            continue
                        else:
                            num = False 
                else:
                    continue
            except:
                continue
        else:
            continue
 
# === CREATES AND UPDATES "RDOM" IN "ATTRDOMV" IN XML FILE ===  

counter = 0
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'rdom' subelement
    labl = attr.find("attrlabl").text                                                       # Field names are crossreferenced to ensure correct order
    for name in rdom_list:                  
        if name[0] == labl:                 
            try:
                attr_rdom = attr.find("attrdomv")   
                if attr_rdom != None:               
                    num = True              
                    counter2 = 0            
                    while num:
                        new_rdom_elem = xml.Element("rdom") 
                        attr_rdom.insert(0, new_rdom_elem)  
                        counter2 += 1
                        if counter2 < len(name[1]):                                         # A counter variable is used to ensure that an 'IndexError' is avoided
                            continue
                        else:
                            num = False 
                else:
                    continue
            except:
                continue
        else:
            continue

# === CREATES AND UPDATES "EDOMV" IN "EDOM" IN XML FILE ===

counter = 0                                        
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'edomv' subelement     
    find_attrdomv = attr.find("attrdomv")           
    if find_attrdomv != None:                       
        for item in find_attrdomv.iter("edom"):     
            new_edomv_elem = xml.Element("edomv")   
            item.insert(0, new_edomv_elem)          
            try:
                edomv_new = edomv_list[counter]         
                new_edomv_elem.text = edomv_new         
                counter += 1
            except IndexError:
                break
    else:
        continue

# === CREATES AND UPDATES "EDOMVD" IN "EDOM" IN XML FILE ===

counter = 0                                         
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'edomvd' subelement               
    find_attrdomv = attr.find("attrdomv")           
    if find_attrdomv != None:                       
        for item in find_attrdomv.iter("edom"):     
            new_edomvd_elem = xml.Element("edomvd") 
            item.insert(1, new_edomvd_elem)          
            try:
                edomvd_new = edomvd_list[counter]       
                new_edomvd_elem.text = edomvd_new       
                counter += 1
            except IndexError:
                break
    else:
        continue

# === CREATES AND UPDATES "EDOMVDS" IN "EDOM" IN XML FILE ===

counter = 0                                             
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'edomvds' subelement                 
    find_attrdomv = attr.find("attrdomv")               
    if find_attrdomv != None:                           
        for item in find_attrdomv.iter("edom"):         
            new_edomvds_elem = xml.Element("edomvds")   
            item.insert(2, new_edomvds_elem)           
            try:
                edomvds_new = edomvds_list[counter]         
                new_edomvds_elem.text = edomvds_new         
                counter += 1
            except IndexError:
                break
    else:
        continue

# === CREATES AND UPDATES "RDOMMIN" IN "RDOM" IN XML FILE ===

counter = 0                                             
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'rdommin' subelement     
    find_attrdomv = attr.find("attrdomv")               
    if find_attrdomv != None:                           
        for item in find_attrdomv.iter("rdom"):         
            new_rdommin_elem = xml.Element("rdommin")   
            item.insert(0, new_rdommin_elem)            
            try:
                rdommin_new = rdommin_list[counter]         
                new_rdommin_elem.text = rdommin_new         
                counter += 1
            except IndexError:
                break
    else:
        continue

# === CREATES AND UPDATES "RDOMMAX" IN "RDOM" IN XML FILE ===

counter = 0                                             
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'rdommax' subelement     
    find_attrdomv = attr.find("attrdomv")               
    if find_attrdomv != None:                           
        for item in find_attrdomv.iter("rdom"):         
            new_rdommax_elem = xml.Element("rdommax")   
            item.insert(1, new_rdommax_elem)            
            try:
                rdommax_new = rdommax_list[counter]         
                new_rdommax_elem.text = rdommax_new         
                counter += 1
            except IndexError:
                break
    else:
        continue

# === CREATES AND UPDATES "ATTRUNIT" IN "RDOM" IN XML FILE ===

counter = 0                                            
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'attrunit' subelement                   
    find_attrdomv = attr.find("attrdomv")               
    if find_attrdomv != None:                           
        for item in find_attrdomv.iter("rdom"):         
            new_attrunit_elem = xml.Element("attrunit") 
            item.insert(2, new_attrunit_elem)       
            try:
                attrunit_new = attrunit_list[counter]       
                new_attrunit_elem.text = attrunit_new       
                counter += 1
            except IndexError:
                break
    else:
        continue

# === CREATES AND UPDATES "ATTRMRES" IN "RDOM" IN XML FILE ===

counter = 0                                             
for attr in detailed.iter("attr"):                                                          # Creates and updates an 'attrmres' subelement   
    find_attrdomv = attr.find("attrdomv")               
    if find_attrdomv != None:                       
        for item in find_attrdomv.iter("rdom"):         
            new_attrmres_elem = xml.Element("attrmres") 
            item.insert(3, new_attrmres_elem)           
            try:
                attrmres_new = attrmres_list[counter]       
                new_attrmres_elem.text = attrmres_new       
                counter += 1
            except IndexError:
                break
    else:
        continue
  
# === WRITES A NEW, UPDATED, XML FILE ===          

tree = xml.ElementTree(root)                                                                # Writes a new metadata xml file    
updated_xml_file = "Updated_Metadata_" + feature_md_short_name
with open (updated_xml_file, "wb") as fileupdate:
    tree.write(fileupdate)
    
# === UPDATES FEATURE WITH NEW XML FILE ===

feature_metadata.importMetadata(updated_xml_file, "FGDC_CSDGM")                             # Updates the feature with the new metadata xml file
feature_metadata.save()                                                                     # Saves the new metadata 
  
