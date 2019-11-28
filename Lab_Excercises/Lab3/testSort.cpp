#include <iostream>
#include <algorithm>
#include <string>
#include <vector>


using namespace std;

class Data
{
public:
    string serverIP;
    vector<int> vclock;
    int clockIndex;
    string msg;

};


//only for server1
bool cmp(Data a, Data b)
{
    if(a.vclock[a.clockIndex] == b.vclock[b.clockIndex])
        return a.serverIP < b.serverIP;
    else
        return a.vclock[a.clockIndex] < b.vclock[b.clockIndex];
    

}

vector<int> makeVc(int s1, int s2, int s3)
{
    vector<int> ret;
    ret.push_back(s1);
    ret.push_back(s2);
    ret.push_back(s3);

    return ret;
}

int main()
{
    vector<Data> d;
    Data temp;
    

    temp.serverIP = "10.1.0.2";
    temp.clockIndex = 1;
    temp.vclock = makeVc(0,2,0);
    temp.msg = "mg";
    d.push_back(temp);

    temp.serverIP = "10.1.0.2";
    temp.clockIndex = 1;
    temp.vclock = makeVc(0,1,0);
    temp.msg = "m1";
    d.push_back(temp);



    temp.serverIP = "10.1.0.3";
    temp.clockIndex = 2;
    temp.vclock = makeVc(1,2,3);
    temp.msg = "N";
    d.push_back(temp);
    
    
    temp.serverIP = "10.1.0.1";
    temp.clockIndex = 0;
    temp.vclock = makeVc(1,0,0);
    temp.msg = "m2";
    d.push_back(temp);

    cout<<"Initially"<<endl;
    for(auto x : d)
    {
        cout<<x.msg<<endl;
    }

    sort(d.begin(), d.end(), cmp);

    cout<<"\n\nFinally"<<endl;
    for(auto x : d)
    {
        cout<<x.msg<<endl;
    }

    return 0;
}