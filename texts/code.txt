using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Cleaner : Employee
{
    [SerializeField] private DirtManager dirtManager;
    [SerializeField] private Job job;

    private void Awake()
    {
        currentGrid = gridManager.GetClosestGridFromWorld(transform.position);

        transform.position = new Vector3(currentGrid.transform.position.x, 
        transform.position.y, currentGrid.transform.position.z);

        EmployeeData data = new EmployeeData();

        data.gender = IdentityCreator.GetGender(70, 30);
        data.name = IdentityCreator.GetName(data.gender);
        data.age = IdentityCreator.GetAge();

        data = (EmployeeData)IdentityCreator.GetRandomAppearance(data);
        SetTex(data.skinTex, data.headTex, data.handTex, data.bodyTex, data.legTex);
        
        data = EmployeeCreator.CreateStat(1, this, data);
        SetStat(typeof(EmployeeData), data);

        transform.parent = employeeManager.transform;
        gameObject.name = data.name + (" (Cleaner)");
    }

    private void Update()
    {
        SetJob(null);

        if(job != null)
        {
            if(job.effectedGrid == currentGrid && path.Count == 0)
            {
                waitingTime = 0f;
                DoJob();
            }
            else if(CheckIfPathAvailable() == false)
            {
                if(waitingTime <= 0.5f)
                {
                    waitingTime += Time.deltaTime;
                }
                else if(waitingTime <= 1.5f)
                {
                    SetJob(job);
                    waitingTime += Time.deltaTime;
                }
                else
                {
                    job.RemoveEmployee(this);
                    job = null;
                    path = new List<GridData>();
                    waitingTime = 0f;
                }
            }
            else
            {
                waitingTime = 0f;

                bool doneGridMove = MoveTowards(path[0], _speed);
                if(doneGridMove)
                {
                    path.Remove(path[0]);
                }
            }
        }
    }

    private void DoJob()
    {
        float deltaTime = Time.deltaTime;
        time = (time - deltaTime >= 0)? time - deltaTime : 0;

        if(time == 0)
        {
            int value = Random.Range((int)((float)_cleaning * 0.75f), (int)_cleaning + 1);

            job.DoWork((uint)value);
            time = 0.25f;
        }
    }

    private void SetJob(Job currentJob)
    {
        if(dirtManager._dirtList.Count > 0 && job == null && currentJob == null)
        {
            for(int i = 0; i < dirtManager._dirtList.Count; i++)
            {
                List<GridData> newPath = Pathfinder.FindPath(gridManager.GetWalkableGrid(), 
                currentGrid, dirtManager._dirtList[i].effectedGrid, true, false);

                if(newPath.Count > 0 || currentGrid == dirtManager._dirtList[i].effectedGrid)
                {
                    if( dirtManager._dirtList[i].SetEmployee(this))
                    {
                        job = dirtManager._dirtList[i];
                        path = newPath;
                        break;
                    }
                }
            }
        }
        else if(currentJob != null)
        {
            List<GridData> newPath = Pathfinder.FindPath(gridManager.GetWalkableGrid(), 
            currentGrid, currentJob.effectedGrid, true, false);

            if(newPath.Count > 0 || currentGrid == currentJob.effectedGrid)
             {
                path = newPath;
            }
        }
    }
}
