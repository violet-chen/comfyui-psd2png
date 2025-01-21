def string_insert(string,find_string,index,insert_string):
    string_list = string.split(find_string)
    string_list.insert(index,insert_string)
    return (find_string.join(string_list))
print(string_insert("a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z",",",2,"this is insert string"))