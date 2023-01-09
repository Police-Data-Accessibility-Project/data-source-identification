#include <iostream>
#include <regex>
#include <set>
#include <fstream>
#include <nlohmann/json.hpp>
using namespace std; // bad form but don't care
using json = nlohmann::json;

//! Contains single testable regex with name
struct labeltest {
    regex rgx;
    string name;

    bool test( std::string url ) const {
        return regex_search( url, rgx );
    }
};

//! Returns contents of single file
std::string file_get_content( const filesystem::path file ) {
    ifstream ifs(file);

    // get first line from file
    string line;
    if( !getline( ifs, line ) )
        throw;

    return line;
}

//! Gets all labels from a directory
vector<labeltest> get_labels( const filesystem::path directory ) {
    vector<labeltest> results;
    for( auto &entry : filesystem::recursive_directory_iterator(directory) ) {
        // skip all non-regular files
        if( !entry.is_regular_file() )
            continue;

        labeltest obj;
        obj.rgx   = std::regex(file_get_content(entry));
        obj.name  = entry.path().filename();
        results.push_back( obj );
    }
    
    return results;
}

int main( int argc, char *argv[] ) {
    // contains the labels we will be testing for
    vector<labeltest> reglib = get_labels( filesystem::path("./regexes") );

    //cout << "[";

    std::string url;
    //bool comma = false;
    while( getline(cin, url) ) {
        set<string> urllabels;

        // iterate through all labels
        for( auto &label : reglib ) {
            // test label
            if( label.test(url) ) {
                // insert label
                urllabels.insert( label.name );
            }
        }

        json output;
        output["url"] = url;
        output["labels"] = urllabels;
        //if( comma )
        //    cout << ",";
        cout << output;

        //comma = true;
    }

    //cout << "]" << endl;

    return EXIT_SUCCESS;
}
