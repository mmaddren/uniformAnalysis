#!/usr/bin/env python2.7
# picardTools.py module holds methods for running picard-tools from a LogicalStep.
#
# Settings required: javaTool (or must be on env PATH), picardToolsDir (or toolsDir)

##### TODO: Resolve path for java.  

import datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    javaVersion = step.ana.getCmdOut(step.ana.getTool('java',orInPath=True) + \
                                     " -version 2>&1 | grep version | awk '{print $3}'", \
                                     dryRun=False,logCmd=False)
    if len(javaVersion) and javaVersion[0] == '"':
        javaVersion = javaVersion[ 1:-1 ] # striping quites
    expected = step.ana.getSetting('javaVersion',javaVersion) # Not in settings then not enforced!
    if step.ana.strict and javaVersion != expected:
        raise Exception("Expecting java [version: "+expected+"], " + \
                        "but found [version: "+javaVersion+"]")
    version = step.ana.getCmdOut(step.ana.getTool('java',orInPath=True) + ' -jar ' + \
                                 step.ana.getDir('picardToolsDir',alt='toolsDir') + \
                                 'SortSam.jar --version', dryRun=False,logCmd=False,errOk=True)
    expected = step.ana.getSetting('picardToolsVersion',version)# Not in settings then not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting picard-tools samSort [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# picard-tools samSort [version: " + version + 
                     "] running on java [version: " + javaVersion + "]")
    return version

def sortBam(step, sam, bam):
    '''
    Sorts sam and converts to bam file.
    '''
    cmd = '{java} -Xmx5g -XX:ParallelGCThreads=4 -jar {picard}SortSam.jar I={input} O={output} SO=coordinate VALIDATION_STRINGENCY=SILENT'.format( \
          java=step.ana.getTool('java',orInPath=True), \
          picard=step.ana.getDir('picardToolsDir',alt='toolsDir'), input=sam, output=bam)

    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'java' sortBam begins...")
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'java' sortBam returned " + str(step.err))
    if step.err != 0:
        raise StepError('sortBam')

