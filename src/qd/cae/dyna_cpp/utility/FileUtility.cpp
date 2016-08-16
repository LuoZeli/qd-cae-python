
#include "FileUtility.hpp"
#include <iostream>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <fstream>
#include <boost/algorithm/string/trim.hpp>
#ifdef _WIN32
	#include <windows.h>
	#include <tchar.h>
	#include <stdio.h>
#else
	#include "glob.h"
#endif


/** Read the lines of a text file into a vector
 * @param string filepath : path of the text file
 *
 * throws an expection in case of an IO-Error.
 */
vector<string> FileUtility::read_textFile(string filepath){

   // vars
   string linebuffer;
   vector<string> filebuffer;

   // open stream
   ifstream filestream(filepath.c_str());
   if (! filestream.is_open())
      throw(string("Error while opening file ")+filepath);

   // read data
   while(getline(filestream, linebuffer)) {
      boost::trim(linebuffer);
      filebuffer.push_back(linebuffer);
   }

   // Check for Error
   if (filestream.bad()){
      filestream.close();
      throw(string("Error during reading file ")+filepath);
   }

   // Close file
   filestream.close();

   // return
   return filebuffer;

}


#ifdef _WIN32

bool FileUtility::check_ExistanceAndAccess(string filepath){


	WIN32_FIND_DATA FindFileData;
	HANDLE handle = FindFirstFile(filepath.c_str(), &FindFileData) ;

	int found = handle != INVALID_HANDLE_VALUE;
	if(found)
	{
		FindClose(handle);
	}

	if(found != 0)
		return true;
	return false;
}


vector<string> FileUtility::globVector(string pattern){

	// get file directory
  string directory = "";
	size_t pos = pattern.find_last_of("/\\");
  if (pos != string::npos)
	  directory = pattern.substr(0,pos) + "/";

	// get files
	vector<string> files;
	WIN32_FIND_DATA FindFileData;
	HANDLE hFind = FindFirstFile(pattern.c_str(), &FindFileData);
	do
	{
		string fname(FindFileData.cFileName);
		files.push_back(directory+fname);

	} while(FindNextFile(hFind, &FindFileData) != 0);
	FindClose(hFind);

	// Sort files
	sort(files.begin(), files.end());

	return files;

}

// linux
#else

bool FileUtility::check_ExistanceAndAccess(string filepath){
  ifstream ifile(filepath.c_str());
  return ifile.good();
}

vector<string> FileUtility::globVector(string pattern){

  glob_t glob_result;
  glob(pattern.c_str(),GLOB_TILDE,NULL,&glob_result);
  vector<string> files;
  for(unsigned int i=0;i<glob_result.gl_pathc;++i){
      files.push_back(string(glob_result.gl_pathv[i]));
  }
  globfree(&glob_result);

  sort(files.begin(), files.end());

  return files;
}

#endif